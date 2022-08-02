## Command list for interacting with IBM Cloud / building Docker images / deploying to Kubernetes

### Logging into IBM Cloud

If you have an API key for the proper account under directory `~/.bluemix` as in `lab-bluemix-cf`:

`make login`

If you need to use a password to login / are having trouble with the API key:

`make pwlogin`

Then enter your email (IBM Cloud account) and password manually.

### Building the Docker image and pushing to IBM Cloud Container Registry

First, use the registry's namespace:

`export NAMESPACE=promotions-devops22`

Then build the Docker image:

`make build`

Then push to the IBM Cloud Container Registry in the appropriate namespace:

`docker push us.icr.io/promotions-devops22/promotions:1.0`

If you want to confirm that this worked:

`ic cr images`

### Managing Kubernetes deployments on IBM Cloud

List all things managed by Kubernetes:

`kc get all`

Delete the entire application in one shot:

`kc delete -f deploy/`

Set up the entire application in one shot:

`kc apply -f deploy/`

Set up elements of the application one at a time (similar for delete):

`kc apply -f deploy/postgresql.yaml`

`kc apply -f deploy/deployment.yaml`

`kc apply -f deploy/service.yaml`

List running services only:

`kc get service`

Check Kubernetes worker node that our application is deployed to:

`ic ks workers --cluster nyu-devops`

The public IP for this worker node + the NodePort of the `promotions` service (from `kc get service`) should display the Promotions application if visited in a web browser.
