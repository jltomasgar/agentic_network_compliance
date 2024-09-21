# Warning control
import warnings
warnings.filterwarnings('ignore')
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool
from agentic_custom_tools import SSHRetriever, SSHConfig


os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o'
os.environ["OPENAI_API_KEY"] = "<your_API_key>"

# Defining instances of the tools
SSH_Retriever_Tool = SSHRetriever()
SSH_Config_Tool = SSHConfig()
FileRead_Tool = FileReadTool()
FileWriter_Tool = FileWriterTool()
DirectoryRead_Tool = DirectoryReadTool()


# Defining the agents

network_retriever = Agent(
    role='Seasoned Network Engineer',
    goal="Connect via SSH to network devices, retrieve their configurations and save them to local files.",
    backstory=(
        "You are a highly skilled network technician, specializing in "
        "remotely accessing routers and retrieving their running configurations."
    ),
    tools=[SSH_Retriever_Tool, FileRead_Tool],
    allow_delegation=False,
    verbose=True,
    memory=False,
)

network_standard_auditor = Agent(
    role="Network configuration auditor",
    goal="Audit the current configurations of the network devices "
         "by comparing them to the Network Standards documents. ",
    backstory=(
        "You are an expert in network configurations and compliance. "
        "Your role is crucial in ensuring that the network devices are "
        "properly configured, based on the Network Architecture Standards."
        "You excel at detecting configurations that do not comply with the Standards."
        "Network Operators and Engineering teams trust your accuracy and reliability "
        "to suggest configuration changes. It is paramount that the suggested changes "
        "are accurate. "
    ),
    tools=[DirectoryRead_Tool, FileRead_Tool, FileWriter_Tool],
    allow_delegation=False,
    verbose=True,
    memory=False,
)

network_configurator = Agent(
    role="Seasoned Network Engineer",
    goal="Deploy network configurations to target devices. ",
    backstory="You are a highly skilled network technician specializing in "
              "deploying configurations to a wide variety of remote network devices. "
              "Network Operators and Engineering teams trust your accuracy and reliability "
              "to deploy configuration changes. "
              ,
    tools=[SSH_Config_Tool, FileRead_Tool, DirectoryRead_Tool],
    allow_delegation=False,
    verbose=True,
    memory=False,
)


# Defining the tasks

network_standard_auditor_task = Task(
    description=(
        "List the contents of the folder ./configs/ where each file's name "
        "represents a network device. Each of those files contains "
        "the current configuration of the network device it represents. "
        "For each of those devices,  audit them against the network standards document stored in the "
        "file ./documents/network_standards.txt. Then, produce an output text "
        "file ./proposed_changes with the proposed changes to all the devices "
        "so that they comply with the configuration standards. "
    ),
    expected_output=(
        "The file './proposed_changes' containing the proposed changes to all the devices "
        "whose configurations are stored in the folder ./configs/. "
        "The file must contain only CLI commands ready to be implemented to the devices, ."
        "grouped by the target device. "
    ),
    output_file="./proposed_changes",
    agent=network_standard_auditor,
    allow_delegation=False,
    verbose=True,
    memory=False,
)

retrieve_configurations_task = Task(
    description=(
        "Read the file network_inventory.csv where you can find a list of remote Cisco devices together with their SSH credentials. "
        "Connect to the remote devices via SSH, retrieve their running configurations and save them to local files. "
    ),
    expected_output='One file for each network device, containing its running configuration.',
    agent=network_retriever,
    verbose=True,
)

Network_configurator_task = Task(
    description=("Read the proposed changes in the file ./proposed_changes and deploy via SSH "
                 "those changes to the relevant remote devices. "
                 "First, connect to the target devices, one by one. "
                 "Second, once connected to a device, make a list of the commands "
                 "to deploy to that target device. Plan commands to go into configuration mode if needed. "
                 " Plan commands to commit or save as needed. "
                 "Third, send the list of commands to the device. "
                 "Finally, disconnect from the device. "
                 "Use the credentials in the file network_inventory.csv for those devices you need to connect to."
                 ),
    expected_output="An indication whether the deployment was successful or not. ",
    agent=network_configurator,
    allow_delegation=False,
    verbose=True,
    memory=False,
)


# Defining the crew

network_crew = Crew(
    agents=[network_retriever, network_standard_auditor, network_configurator],
    tasks=[retrieve_configurations_task, network_standard_auditor_task, Network_configurator_task],
    process=Process.sequential,
    verbose=True
)

result = network_crew.kickoff()
print(result)
