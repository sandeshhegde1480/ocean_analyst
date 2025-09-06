import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import ast
from termcolor import colored
import json
from . import analyser as imp
import pandas.core.frame
from langchain_ollama import OllamaLLM
from json_repair import repair_json

# VARIABLES
sentiment_dict = {
    'analyse': 'If the user asks to analyse the dataset(s), or asking for comparing two or more than two datasets or asks the details of the dataset(s) or anything meant to operate like min, plot etc., on datasets',
    'other': 'If the user asks or says anything else than to analyse'
}
operations = ['overall analysis', 'compare', 'min', 'max', 'dot-plot', 'bar-plot', 'box plot', 'pie chart', 'mean', 'median', 'mode', 'heatmap']

parameter_definition = {
    "dataframe_count": "The total number of dataframes. The value either can be None or can be a natural number (Example: 'dataframe_count': 2 or 'dataframe_count': 1 or 'dataframe_count': None). Count the total number of dataframes mentioned by the user text and update the value.",
    "dataframes": "It is the list of the dataframes mentioned by the user text. The value either can be an empty python list or can be a python list of names of dataframes (Example: 'dataframes': [] or 'dataframe': ['dataframe1, dataframe2'......]). Carefully analyse the user text for the name of the dataset and/or dataframe and/or datasheet and/or similar.",
    "operations": "It is the structured details of the operation, which the user asked for. The value can be empty list or list of dictionaries. If any operations are given by the user, among the given {operations}, update the value.",
    "operation_name": "It is a member of 'operations', which should hold the name of the operation. The value cannot be None if the user asks for any operations. ",
    "df": "It is the list of dictionaries, which contain the details of the dataframe mentioned by the user",
    "dataframe_name": "It is the name of the dataframe, which the user mentions for the corresponding operation. Either the value can be None or a string, i.e., the name of the dataframe.",
    "axis": "It is the list of two members. Update the value if the user explicitly mentions the axis. The first member is the x axis column and the second member will be y axis column",
    "columns": "It is a list which holds the name of all columns, on which the operation should occur. If no columns are mentioned by the user and operation is mentioned, then return the value as 'all'",
}
parameter_structure = {
    'dataframe_count': None,
    'dataframes': [],
    'operations': [
        {'operation_name': None, 'df': [
            {'dataframe_name': None, 'columns': [], 'axis': [None, None]}
        ]}
    ]
}
default_parameters = {}
class Agent:
    user = ''
    last_reply = ''
    chat_status = 0
    message = ''
    initial = 0
    parameters = default_parameters

    def sys_print(self, text):
        print(colored(text, color='blue'))

    def rep_print(self,text):
        print(colored(text, color='yellow'))

    def st_print(self,text):
        print(colored(text, color='red'))

    # FUNCTIONALITIES
    def sentiment_analysis(self,message_: str | None = None) -> str | None:
        self.st_print('Entered sentiment analysis ---------')
        llm = OllamaLLM(model = 'gemma3:4b', temperature = 0)
        template = """
          You are an AI assistant. Analyse the following text and classify it into the given sentiments.
          Text: {text}
          Sentiments:
          {sentiment_dict}

          Example:
          After analysing the Text, return the sentiment. If the sentiment is matching two or more than two in the given, then return in a single python list like ['other', 'analyse', ......]  If sentiment doesn't match, return as 'None'. If the sentiment of a part of the text matches and other part didn't match, then return as [matches sentiment 1, 'None', matched sentiment 2, ...........]
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = message_
        response = chain.invoke({"text": human_message, "sentiment_dict": sentiment_dict})
        return response

    def post_sentiment_analysis(self,sentiment_):
        try:
            s = sentiment_.replace('python', '').replace("```", '')
            sentiment_ =  s.strip()
            sentiment_ = ast.literal_eval(sentiment_)
            self.sys_print(type(sentiment_))
            if sentiment_ is None:
                print('it is None')
                reply_ = self.reply_handler(params=self.parameters, message_= self.message)
                return reply_
            elif isinstance(sentiment_, list):
                self.sys_print('it is list')
                reply_ = self.reply_handler(params=self.parameters, message_=self.message, sentiment_=sentiment_)
                return reply_
            elif type(sentiment_) is str:
                self.sys_print('it is string')
                reply_ = self.reply_handler(params=self.parameters, message_=self.message, sentiment_=[sentiment_])
                self.rep_print(reply_) if isinstance(reply_, str) else self.sys_print(reply_)
                return reply_

        except Exception as e:
            self.st_print(e)
            if type(sentiment_) is str:
                self.sys_print('it is string')
                reply_ = self.reply_handler(params=self.parameters, message_=self.message, sentiment_=[sentiment_])
                self.rep_print(reply_) if isinstance(reply_, str) else self.sys_print(reply_)
                return reply_

    def reply_handler(self, params: dict, message_: str, sentiment_: list | None = None):
        print(sentiment_)
        self.st_print('Entered reply handler ---------')
        if isinstance(sentiment_, list):
            self.st_print('received_sentiment')
            if 'analyse' in sentiment_:
                return self.operation_analysis(message_=message_, params=params)
            else:
                command = f"The user said {message_}. Return appropriate reply. It should be different from your last reply (mentioned in variable)"
                return self.req_llm(var = self.last_reply, command=command, chit_chat =1)

    def operation_analysis(self,message_: str,  params: dict | None = None):
        self.st_print('Entered operation_analysis')
        llm = OllamaLLM(model = 'gemma3:4b', temperature = 0)
        self.chat_status = 1
        template = """
          You are an AI assistant. Analyse the following text and return as directed:
          Text: {text}
          The user is asking to analyse a dataset. You also given what are the details provided by the user so far (2nd in the references).
          
          Directions:
          Now, you need to update the values of {default_parameters} for the following and return the values as {parameter_structure}:
          {parameter_definition}
        
          references:
          1. operation list: {operations}
          2. previous given parameters: {params}
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = message_
        response = chain.invoke({"text": human_message, "operations": operations, "params": params, "default_parameters": default_parameters, "parameter_definition": parameter_definition, "parameter_structure": parameter_structure})
        json_struct = None
        if response:
            print('Type of response: ', type(response))
            print(response)
            if isinstance(response, str):
                json_struct = response.strip().removeprefix("```json").removesuffix("```").strip()
                json_struct = repair_json(json_struct)

            parameters_ = json.loads(json_struct)
            if parameters_:
                self.parameters = parameters_
                return self.requirement_handler(parameters_)
            else:
                return None

    def requirement_handler(self,params: dict | None = None):
        self.st_print('Entered requirement handler --------------------')
        requirements_ = []
        if params:
            pass
        if requirements_:
            req, quest = self.request_requirements(req=requirements_)
            return quest
        else:
            return self.operation_assigner(params = params)

    def request_requirements(self,req: list):
        question = ''
        requirement = req.pop(0)
        command = 'Phrase a question to ask/request/provide the variable from a user'
        if isinstance(requirement, str):
            question = self.req_llm(requirement, command)
        elif isinstance(requirement, dict):
            question = self.req_llm(f'No columns mentioned for {list(requirement.keys())[0]}', command)
        return req, question

    def req_llm(self,var, command: str, chit_chat: int|None = None):
        llm = OllamaLLM(model = "mistral", temperature= 1)
        template = """
          You are an AI assistant called Ocean Analyst created by sanh on 9th September 2025,and you generates only the answer to the asked questions and what mentioned is in the command. By the way, user name is {user_}
          Command: {command}
          Variable: {var} 
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = self.message
        response = chain.invoke({"command": command, "var": var, "user_": self.user})
        self.last_reply = response if chit_chat == 1 else ''
        return response

    def operation_assigner(self,params: dict):
        print(params)
        self.sys_print('assigning')
        directories = os.listdir(r"C:\Users\91827\Desktop\data\230927")
        print('directories')
        reports = {}
        operations_ = [list(x.keys())[0] for x in params['opted_operation']]
        if 'overall analysis' in operations_:
            dataframes = params['opted_operation'][operations_.index('overall analysis')]['overall analysis']
            paths = []
            for i in dataframes:
                if i in directories:
                    paths.append(os.path.abspath(i))
            reports['overall analysis'] = imp.overall_analysis(paths)
        if 'compare' in operations:
            dataframes = params['opted_operation'][operations_.index('overall analysis')]['overall analysis']
            paths = []
            for i in dataframes:
                if i in directories:
                    paths.append(os.path.abspath(i))
            reports['overall analysis'] = imp.overall_analysis(paths)
        # columns = params['opted_operation'][operations_.index('overall analysis')]['overall analysis']['dataframes']
        return reports

    def implementor(self, message, user):
        bot_reply  = {'content' : [], 'type': ''}
        print('Implementor')
        self.message = message
        self.user = user
        sentiment = self.sentiment_analysis(message)
        print('analysed sentiment is : ', sentiment)
        reply = self.post_sentiment_analysis(sentiment)
        print(reply)

        if isinstance(reply, str):
            bot_reply['type'] = 'list'
            bot_reply['content'] = [reply]

        elif isinstance(reply, list):
            bot_reply['type'] = 'list'
            bot_reply['content'] = reply

        elif isinstance(reply, dict):
            self.st_print(reply)
            for i in reply.keys():
                print(reply[i])
                for x in reply[i].keys():
                    bot_reply['content'].append(reply[i][x].to_html(classes="table table-striped", index=False))
            bot_reply['type'] = 'list'

        else:
            bot_reply['type'] = 'list'
            bot_reply['content'] = ["Sorry, I got confused there 🤔"]
        return bot_reply