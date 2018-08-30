$ pytest tests/orcid -s --env prod

The Makefile and Docker stuff was made in order to run the monitoring
test_actually_count_celery_queues in Jenkins, but unfortunately Jenkins
seems not to have Docker:
$ make celery-monitor/prod
