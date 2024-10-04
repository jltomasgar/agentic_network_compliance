# Warning control
import warnings
warnings.filterwarnings('ignore')
from langchain_core.prompts import ChatPromptTemplate
from langchain.globals import set_verbose
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import FileManagementToolkit
from agentic_custom_tools_langchain import SSHRetriever, SSHConfig

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key="your_API_key",
)
set_verbose(True)

#Prepare the agentic tools
File_Tools = FileManagementToolkit(
    root_dir=str('./'),
    selected_tools=["read_file", "write_file", "list_directory"],
).get_tools()
File_Read_Tools = FileManagementToolkit(
    root_dir=str('./'),
    selected_tools=["read_file", "list_directory"],
).get_tools()
SSH_Retriever = SSHRetriever()
SSH_Config = SSHConfig()

# Agent 1
tools1 = [SSH_Retriever]+File_Tools
prompt1 = ChatPromptTemplate.from_messages([
    ("system", "You are a network engineer with deep expertise in managing and retrieving configurations from remote network devices. "
               "You are also an expert on reading files from the local system, in particular CSV files."),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])

agent1 = create_tool_calling_agent(llm, tools1, prompt1)
agent_executor1 = AgentExecutor(agent=agent1, tools=tools1)
output_agent1 = agent_executor1.invoke({"input": "Read the file network_inventory.csv where you can find a list of remote Cisco devices together with their SSH credentials. "
                                "Connect to the remote devices via SSH, retrieve their running configurations. "
                                })
print(output_agent1['output'])

# Agent 2
prompt2 = ChatPromptTemplate.from_messages([
    ("system", "You are a network engineer with deep expertise auditing configurations of network devices. "
               ),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])
tools2 = File_Tools
agent2 = create_tool_calling_agent(llm, tools2, prompt2)
agent_executor2 = AgentExecutor(agent=agent2, tools=tools2)
output_agent2 = agent_executor2.invoke({"input": 
    "Read our Standards documentation is stored in the file ./documents/network_standards.txt. "
    "Then, read all the Cisco configurations in the folder ./configs, each file belongs to a different device. "
    "Finally, audit the configurations you have read, according to the Standards documentation, and suggest what CLI changes "
    "are necessary on each device so that they are compliant with the Standards. The proposed changes must be only CLI commands "
    "to be deployed on each device. Store those changes in the file ./proposed_changes. "
                                })
print(output_agent2['output'])

# Agent 3
prompt3 = ChatPromptTemplate.from_messages([
    ("system", "You are a network engineer with deep expertise in managing and deploying configurations to remote network devices. "
               ),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])
tools3 = [SSH_Config]+File_Read_Tools
agent3 = create_tool_calling_agent(llm, tools3, prompt3)
agent_executor3 = AgentExecutor(agent=agent3, tools=tools3)
output_agent3 = agent_executor3.invoke({"input": 
    "Read the proposed changes in the file ./proposed_changes and deploy via SSH those changes to the relevant remote devices. "
    "First, connect to the target devices, one by one. "
    "Second, once connected to a device, make a list of the commands to deploy to that target device. Go into configuration mode if needed. Commit or save as needed. "
    "Third, send the list to the device. "
    "Finally, disconnect from the device. "
    "Use the credentials in the file network_inventory.csv for those devices you need to connect to."
                                })
print(output_agent3['output'])

