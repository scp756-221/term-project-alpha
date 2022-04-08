
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