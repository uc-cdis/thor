curl -X POST $SLACK_WEBHOOK \
    -H 'Content-Type: application/json'\
    -d "{'text':'Release $RELEASE_VERSION was successfully published. '}"