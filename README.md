
# CMPT 756 - Distributed and Cloud Systems - Spring 2022

This repository is the project for CMPT 756 - Distributed and Cloud Systems. For this project we have used Amazon Web Services to cater to the compute requirements. 


## Contributors

- [Aditya Panchal](https://github.com/aadityapanchal)
- [Divye Maheshwari](https://www.github.com/divyemaheshwari)
- [Hemang Bhanushali](https://www.github.com/ihemangb07)
- [Manav Patel](https://www.github.com/manav113)
- [Priyanka Manam](https://www.github.com/priman15)


## Amazon Web Services(AWS) Setup
Since the project is using AWS for its execution, you would require an AWS account to run it. 
If you do not already have an AWS account click [here](aws.amazon.com)

## Code Structure

| Folder Name | Description |
| :-------- | :------------------------- |
| ci | Continuous Integration related files |
| cluster | EKS cluster configuration related files |
| db | Database service for accessing AWS DynamoDB |
| gatling | Files to generate synthetic load for services |
| loader | Load DynamoDB with fixtures for the three services |
| logs | Logs files are saved here to reduce clutter |
| s1 | Users Service |
| s2 | Music service |
| s3 | Playlist service |
| tools | 'Tools' container to develop new services locally |

## System Architecutre
![System Diagram](https://github.com/scp756-221/term-project-alpha/blob/s3-playlist/System-diagram.png "System Architecture Diagram")

| Service | Short name     | Description                |
| :-------- | :------- | :------------------------- |
| Users | s1 | List of users |
| Music | s2 | Lists of songs and their artist |
| Database | db | Interface to key-value store |
| Playlist | s3 | List of Playlists |

## How to run the system


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

### Create a new namespace
Kubernetes uses a namespace to organize applications. Begin by creating a namespace c756ns and setting it as the default:
~~~
/home/k8s# kubectl create ns c756ns
/home/k8s# kubectl config set-context --current --namespace=c756ns
~~~

`Provisioning` : Installing the course's sample application and the components required. It can be done by running 
~~~
/home/k8s# make -f k8s.mak provision
~~~


### To get the link to the Grafana Dashbaord 
~~~
/home/k8s# make -f k8s.mak grafana-url. 
~~~

### To login into the dashboard, use the following credentials
- User: `admin`
- Password: `prom-operator`

### Open the `c756 transactions` dashboard
After signon, you will see the Grafana home screen. Navigate to our dashboard by hovering on the “Dashboards”(four squares) icon on the left. Select “Browse” from the menu. This will bring up a list of dashboards. Click on `c756 transactions`.


### Send load to the application from Gatling
Run the following commands with 30 as NUM-USERS. This will generate a load for the relevant microservice 
~~~
/home/k8s# tools/gatling-n-music.sh <NUM-USERS>
/home/k8s# tools/gatling-n-user.sh <NUM-USERS>
/home/k8s# tools/gatling-n-playlist.sh <NUM-USERS>
~~~

### Manually scale the system
Add more pods to a service. Put the required count of pods in the `replica-count`.
Example: /home/k8s# kubectl scale deployment/cmpt756s3-v1 --replicas 5
~~~
/home/k8s# kubectl scale deployment/cmpt756s3-v1 --replicas <replica-count>
~~~


Add more worker node. Put the required worker node count in the `node-count`
Example: eksctl scale nodegroup --name=worker-nodes --cluster aws756 --nodes 5
~~~
/home/k8s# eksctl scale nodegroup --name=worker-nodes --cluster aws756 --nodes <node-count>
~~~

### Autoscale the system

We will deploy the metrics server using [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server).
~~~
/home/k8s# kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.5.0/components.yaml
~~~
Set threshold for required metrics above which the pods will autoscale
Example: /home/k8s# kubectl set resources deployment cmpt756s3-v1 -c=cmpt756s3-v1 --limits=cpu=80m,memory=64Mi
~~~
kubectl set resources deployment <service-name> -c=<service-name> --limits=cpu=80m,memory=64Mi
~~~

Setting minimum and maximum number of pods to be autoscaled. 
Example: /home/k8s# `kubectl autoscale deployment cmpt756s3-v1 --min=2 --max=100`
~~~
/home/k8s# kubectl autoscale deployment <service-name> --min=2 --max=100
~~~

### Kill the Gatling load
~~~
./tools/kill-gatling.sh
~~~

### Stop the EKS cluster
~~~
make -f eks.mak stop
~~~

## Acknowledgements

 - A major part of the code base has been taken from [c756-exer](https://github.com/scp756-221/c756-exer) repository. This repository is developed and maintained by the teaching team of CMPT 756 at Simon Fraser University. We highly appreciate their efforts and constant improvement to the code.
 

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


###  List the tables in DynamoDB
~~~
$ aws dynamodb list-tables
~~~

### To create/delete these tables by way of AWS’ CloudFormation (AWS’ IaC technology):
~~~
# create a stack that encapsulate the 2 tables
$ aws cloudformation create-stack --stack-name <SomeStackName> --template-body file://path/to/cluster/cloudformationdynamodb.json 
# delete the stack
$ aws cloudformation delete-stack --stack-name <SomeStackName>
~~~

### Check if the replicas were allotted to a service
~~~
kubectl describe deploy/<service-name>
~~~

### Check the number of worker-nodes running currently
~~~
kubectl get nodes
~~~

