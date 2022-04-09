
# CMPT 756 - Distributed and Cloud Systems - Spring 2022

This repository is the project for CMPT 756 - Distributed and Cloud Systems. For this project we have used Amazon Web Services to cater to the compute requirements. 


## Contributors

- [Aditya Panchal](https://github.com/aadityapanchal)
- [Divye Maheshwari](https://www.github.com/divyemaheshwari)
- [Hemang Bhanushali](https://www.github.com/ihemangb07)
- [Manav Patel](https://www.github.com/manav113)
- [Priyanka Manam](https://www.github.com/priman15)


## Demo

- [Demo/YoutTube Link]()


## Amazon Web Services(AWS) Setup
Since the project is using AWS for its execution, you would require an AWS account to run it. 
If you do not already have an AWS account click [here](aws.amazon.com)
## System Architecutre

| Service | Short name     | Description                |
| :-------- | :------- | :------------------------- |
| Users | S1 | List of users |
| Music | S2 | Lists of songs and their artist |
| Database | DB | Interface to key-value store |
| Playlist | S3 | List of Playlists |

## How to run the system

- Prerequisites: 

###  1. Clone the project

```bash
  git clone https://github.com/scp756-221/term-project-alpha 
```

###  2. Instantiate the template files

#### Fill in the required values in the template variable file

Copy the file `cluster/tpl-vars-blank.txt` to `cluster/tpl-vars.txt`
and fill in all the required values in `tpl-vars.txt`. You will need values like your AWS keys, your GitHub signon, and other identifying
information.  See the comments in that file for details. Note that you
will need to have installed [Gatling](https://gatling.io/open-source/start-testing/) first, because you
will be entering its path in `tpl-vars.txt`.

###  3. Download and Start Docker Application
 - In your system, download and launch [Docker Desktop](https://www.docker.com/products/docker-desktop/).
 - Open Unix Terminal at the location of your cloned code.

#### Start Tools Container

Once you have filled in all the details, open terminal at the location where you cloned the repositor and run the following command
~~~
$ tools/shell.sh
~~~
This will start a container on your system. Your terminal will show `.../home/k8s...#` as the current prompt.


#### Instantiate the templates
Next you need to instantiate every template file. In the tools container, run this command:
~~~
$ make -f k8s-tpl.mak templates
~~~

This will check that all the programs you will need have been
installed and are in the search path.  If any program is missing,
install it before proceeding.

The script will then generate makefiles personalized to the data that
you entered in `clusters/tpl-vars.txt`.

#### Creating a Cluster
Start up an Amazon EKS cluster as follows:
~~~
/home/k8s# make -f eks.mak start
~~~
This is a slow operation, often taking 10–15 minutes. See Appendix for more operations for managing cluster. 

#### Installing the service mesh istio
`istio` is a service mesh that was conceived concurrently with k8s. But for various reasons, it was ultimately pulled out of k8s and developed as an independent project.

#### Create a new namespace

Create a new namespace named `c756ns` inside each cluster and set each context to use it:
~~~
/home/k8s#  kubectl config use-context aws756
/home/k8s#  kubectl create ns c756ns
/home/k8s#  kubectl config set-context aws756 --namespace=c756ns
~~~


#### Installing the service mesh istio
istio is installed into each cluster only once but it will only operate within specific namespaces that you choose. A k8s namespace is a cluster-level construct that organizes the resources within your cluster.

To use istio with an application, you create a namespace for your application, label the namespace for istio, and install your application into this namespace.

To install Istio and label the c756ns namespace:
~~~
/home/k8s# kubectl config use-context aws756
/home/k8s# istioctl install -y --set profile=demo --set hub=gcr.io/istio-release
/home/k8s# kubectl label namespace c756ns istio-injection=enabled
~~~
See Appendix for more operations within istio


#### Accessing the AWS Cluster
The required external IP address of the cluster can be fetched using kubectl:
~~~
/home/k8s# kubectl -n istio-system get service istio-ingressgateway | cut -c -140
~~~
Sample Output:
~~~
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP                                                              PORT(S)      
istio-ingressgateway   LoadBalancer   10.100.255.11   a844a1e4bb85d49c4901affa0b677773-127853909.us-west-2.elb.amazonaws.com   15021:32744/T
~~~
The `EXTERNAL-IP` is the entry point to the cluster.

#### Building your Docker Images
Now, we need to build the containers and push them to the container registry. We are using GitHub Container Registry for this project. 

We build four services as follows:
| Service | Image name |
| :-------- | :------- |
| Users | cmpt756s1 |
| Music | cmpt756s2 |
| Playlist | cmpt756s3 |
| Database | cmpt756db |

To build the images: 
~~~
/home/k8s# make -f k8s.mak cri
~~~

#### Grant public access to the images
Switch your container repositories to public access. Refer to [GitHub’s documentation](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility#configuring-visibility-of-container-images-for-your-personal-account).

#### Deploying the four services to AWS

DB: The database service, providing persistent storage to the three higher-level services, S1, S2 S3.
DynamoDB: An Amazon service, called by DB to actually store the values.

Gateway: A link between S1, S2, S3 and the external world.
To run this, we first need to start the gateway, database, users, music and playlist services. This can be achieved by the following command:

~~~
/home/k8s# make -f k8s.mak gw db s1 s2 s3
~~~

#### To complete the setup for all the services, we need to initialize DynamoDB and load it with mock data. This mock data is loaded from exisitng csv files:
~~~
/home/k8s# make -f k8s.mak loader
~~~
This step builds and pushes another image `cmpt756loader` to GitHub Container Registry. Set the access for this new image to public as done before. 

## Appendix

### Additional targets to manage AWS cluster:

| Service | Description                |
| :-------- | :------------------------- |
| `make -f eks.mak start` | create your EKS cluster |
| `make -f eks.mak stop` | delete your EKS cluster |
| `make -f eks.mak down` | delete an EKS cluster’s nodegroup |
| `make -f eks.mak up` | reate a nodegroup for an EKS cluster whose group was previously deleted |
| `make -f eks.mak status` | check on the status of your EKS cluster |
| `make -f eks.mak ls` | ist all EKS clusters and their node groups |
| `make -f eks.mak cd` | make the EKS cluster your current cluster (when runnning clusters from multiple vendors) |


### kubeconfig
Upon completion of the creation of the cluster, to see the summary of the current environment (also known as kubeconfig) by:
~~~
/home/k8s#  kubectl config get-contexts
CURRENT   NAME     CLUSTER                      AUTHINFO                         NAMESPACE
*         aws756   aws756.us-west-2.eksctl.io   AWSID@aws756.us-west-2.eksctl.io   
~~~
where `AWSID` will be your AWS userid.

### Managing cloud costs

To reduce cost, you can either delete the cluster entirely `(make -f eks.mak stop)` or delete the nodegroup.
Either of these command will again take a relatively long time (10+ min) to complete.
~~~
To delete the nodegroup of your cloud cluster:
/home/k8s#  make -f VENDOR.mak down
~~~
~~~
To recreate the node-group of your cloud cluster:
/home/k8s#  make -f VENDOR.mak up
~~~


### Remove the label from istio
~~~
/home/k8s# kubectl label namespace c756ns istio-injection-
~~~

### To view the logs of any service. Kubernetes offers a similar command:
~~~
/home/k8s# kubectl logs --selector app=cmpt756s2 --container cmpt756s2 --tail=-1
The --selector parameter specifies the pod name and the --container parameter specifies the container name (both of which are cmpt756s2), while --tail=-1 requests that the entire log be returned, no matter how long.
~~~
