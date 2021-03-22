# Welcome!

This is a cryptocurrency tracker that uses Python to get latest prices every minute,
store them in DynamoDB and expose the data via a REST service.

## How to run?

Using docker-compose (assuming you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed)

Run the following from the root folder of this repo: 
```
docker-compose up
```

The docker-compose yaml is using version 3.8, the daemon version was 

The services can also be run separately. They were built using Python 3.9. Other versions may work but were not tested.

```
python3 -m venv venv 
source venv2/bin/activate
pip3 install -r service/requirements.txt
python3 -m service.api
pip3 install -r fetcher/requirements.txt
python3 -m fetcher.main
```


TODO Caveats: 
- I haven't found a way to easily run dynamoDB locally without Docker, instructions can be found [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)
if needed.
- Minor changes have to be made to run the code without docker-compose, notably `http://dynamodb-local:8000` should be replaced with localhost.

## Architecture

![Architecture diagram](/docs/schematic.png?raw=true)

There are 3 parts to this tracker: 

1. The data fetcher - this is a scheduled python script which makes async HTTP requests to Cryptowat.ch 
  to get the latest prices for each currency pair
  
2. AWS DynamoDB: This is a local version of DynamoDB. Data is structured as follows:
  - currency pair as HASH key
  - timestamp as RANGE key
  - value has price
  
3. The backend service: This is a Flask application which exposes REST endpoints. Some examples:
  - latest price for currency pair: http://127.0.0.1:5000/service/v1/pair/btcusd
  - last day's prices for currency pair: http://127.0.0.1:5000/service/v1/pair_last_dat/btcusd
  - standard deviation for currency pair: http://127.0.0.1:5000/service/v1/std/btcusd
  - rank several currency pairs: http://127.0.0.1:5000/service/v1/rank?pair=btcusd&pair=ethusd&pair=daiusd

Some assumptions:

- only bitfinex data was used
- jobs are scheduled using time.sleep(60), so it's not perfectly scheduled once a minute
- some important things are missing such as error handling, some useful endpoints like `/all`, and others

## Next steps

### Scalability

For this implementation, I chose to prioritize building the skateboard ahead of the car, 
rather than building a full-fledged engine, wheels, body, etc.

Hopefully, it should be easier to iterate on a simpler concept for future enhancements 
rather than build something complex from the get-go.

#### Potential enhancements:

1.  Use a more robust scheduler

I used a simple `time.sleep(60)` to run the fetcher once a minute. 
After running this several times, the scheduling would eventually veer away from being 
exactly once a minute, due to the time it takes to make the requests and ingest to the DB. Airflow would be an easy way to improve this. 
To do this, we would need to call the appropriate function (perhaps `run_async`) as part of our DAG and schedule it as needed. 
I'd suggest [AWS's managed service](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html) to 
reduce the amount of effort on our side. Currently, a single fetch of all the currencies (for bitfinex) 
uses asyncio which on my machine took less than 4 seconds.

If we wanted to increase the frequency, Airflow has the ability to [autoscale workers](https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-autoscaling.html),
so we could schedule the job by the number of seconds if needed. If we wanted even higher frequency, I'm not sure if Airflow would be the best tool for the job.
We may want to consider other options such as not running the fetcher on a defined schedule, but rather provision workers
to run the jobs in a distributed way, and consistently stream the data as it comes. This would require some investigation 
on my end, since I haven't seen Airflow being used for high frequencies.

2. Caching aggregates

The current solution has to fetch the last 24 hours of data in order to compute the standard deviation. 
This [Stack Overflow answer](https://math.stackexchange.com/questions/102978/incremental-computation-of-standard-deviation)
seems like a potentially interesting solution to incrementally compute standard deviation, though I didn't have a chance to dive deeper yet.

Other than that, some simpler aggregates could be saved on write such as min/max over a period, averages, etc.

If we expect traffic from clients to increase, we could (a) add caching using something like Redis, caching the URL 
requests along with timestamps, with a TTL of 1 
minute to reduce the number of repeat computations,
and (b) also add a load-balancer in front of the back-end to reduce load.

### Testing

I implemented some very simple unit tests. To make this more robust, it would be nice to add:

- integration tests, for end-to-end functionality. This could be in the form of fixtures data being loaded to the database,
  and assertions made on results being returned by the API.
- some heartbeat checks on our services to check they are alive and healthy. I'm less familiar with this part of the stack, 
  but have heard good things about [Grafana](https://grafana.com/) and would implement SLA tracking using something similar. 
- some quality testing on our data (we could regularly check on some metrics such as: freshness of latest prices for each currency, etc)

### Feature requests: alerts

If we are using Airflow, I'd propose to add an additional scheduled job to run our "alert checks". This job would run through 
the checks independently of the backend service so as not to slow down the application for users.

The checks themselves would be defined by users and would be stored in a database 
(it may be easier to structure this as a more relational data structure, along with other user-related information).
Our new job would then run through the necessary checks and send out email/slack/Pagerduty/etc. notifications as configured by the user.

### Other enhancements

- CI/CD: I didn't have a chance to set it up, but I think this would be an easy way to get 
  to a fast feedback cycle and be able to iterate on the product more easily. There are many tools for this,
  such as [Drone CI](https://www.drone.io/) and many others. A YAML file is used to define the tasks in the pipeline.
- Data types and schemas: right now this implementation is passing dicts and json around between modules, 
  I would define objects and schemas to make the code more easily readable
  and maintainable, and make the service more robust.
- Error handling: This is very much lacking in my current solution and would also add robustness to the service.
- Evaluate other APIs: They might be able to offer timestamped data which could add to our accuracy (right now I used timestamps from the request time).
  It may make sense also to find an API which provides history prices which could help to backfill jobs if our service goes down.
- Making our service idempotent: Right now, the fetcher loads data "as it comes". We may want to make the job idempotent,
  i.e. if we run the job several times, we may not want to reingest data for the same time ranges.
- Add some more intuitive REST arguments, such as timestamps rather than pair_last_day
