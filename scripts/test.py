from gocd import Server

import json

USERNAME = 'admin'
PASSWORD = 'badger'
PIPELINE_NAME = 'up42'
PIPELINE_COUNTER = 1
STAGE_NAME = 'up42_stage'
STAGE_COUNTER = 1

server = Server('http://localhost:8153', USERNAME, PASSWORD, "py-gocd.log")

pipeline = server.pipeline(PIPELINE_NAME)

response =  pipeline.schedule(return_new_instance=True, maximum_backoff_time=100, backoff_time=10)

# response = pipeline.status()
# print(response.is_ok)

# groups = server.pipeline_groups()
# all_pipeline_groups = groups.get_pipeline_groups().payload['_embedded']['groups']
# all_pipeline_groups_name = all_pipeline_groups[0]['name']
#
# print(all_pipeline_groups_name)

# response = pipeline.instance(41)
# print(response.is_ok)
# print ("hello")

# response = pipeline.release()
# print(response)

# response = pipeline.history()
# print(response.is_ok)
# response.payload["pipelines"]

# history = response["pipelines"][0]

# print(history.is_ok)
# response = pipeline.history(10);
# print(response)
# print(response.is_ok)

# stage = server.stage('up42', 'up42_stage', 40)
# response = stage.history()
# response= stage.run()
# response = stage.instance(40)
# print(response.is_ok)

# stage = server.stage('PHP', 'Configure', 36)
# response= stage.cancel(16)
# print(response.is_ok)

# response = pipeline.pause('Admin says no work for you.')
# print(response.is_ok)

# unpause_response = pipeline.unpause()
# print(unpause_response.is_ok)

# response = pipeline.schedule()
# print(response.is_ok)

# response = pipeline.schedule({"name":"username", "value":"bob"})
# print((response.is_ok))
