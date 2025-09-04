# health-check-dashboard
A simple DevOps project that monitors websites availability and response time

to run the program:
1. run the following commends on powershell from the main folder (health check dashboard folder):

      simple (without saving sites)

                                 docker build -t health-check-dashboard .
                                 docker run --name hcd -p 5000:5000 health-check-dashboard


      advanced (with saving sites)
   
                                 docker build -t health-check-dashboard .
                                 docker run --name hcd -p 5000:5000 `
                                 -e DATA_DIR=/data `
                                 -v ${PWD}\data:/data `
                                 health-check-dashboard

*note: if you are switching mode you should stop and delete the container using:


                                 docker stop hcd; docker rm hcd

3. open the folowing URL:
                                      http://localhost:5000/

4. open the folowing URL for monitoring:
                                      http://localhost:5000/metrics
