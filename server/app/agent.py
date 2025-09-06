import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import ast
from termcolor import colored
import json
from . import analyser as imp
import pandas.core.frame

# API
os.environ["GOOGLE_API_KEY"] = "API KEY"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
# VARIABLES
sentiment_dict = {
    'greetings': 'only if the user is saying good night, good after noon, hi, hello and/or similar. Not asking how are you or how you doing or and similar',
    'status_based': 'only if the user is saying how are you or how you doing or and similar.',
    'analyse': 'If the user asks to analyse the dataset(s), or asking for comparing two or more than two datasets or asks the details of the dataset(s) or anything meant to operate on datasets',
    'end convo': "If the user's sentiment says to end the chat by any means, like saying gratitude and/or anything similar"
}
operations = ['overall analysis', 'compare', 'min', 'max', 'dot-plot', 'bar-plot', 'box plot', 'pie chart', 'mean',
              'median', 'mode', 'heatmap']

parameter_definition = {
    'dataframe_count': 'Total number of dataframes, user targeting (the value can be either None or a natural number)',
    'dataframes': 'paths or names of the dataframes (the value can be either None or a list: [path1, path2, .......] or [name1, name2, ....................])',
    'opted_operation': 'operation specified by the user (the value can be either None or a list of dictionaries: [operation1 : {{[dataframe1, dataframe2, ......]}}, operation2: {{[dataframe1, dataframe2, ......]}}]). The operation should be classified from the list of operations given below. If an operation is mentioned apart from the list, write None accordingly',
    'x_axis': 'column name which has to be on x-axis in the graphs or plots (applicable on some operations). The value can be either None or a string',
    'y_axis': 'column name which has to be on y-axis in the graphs or plots (applicable on some operations). The value can be either None or a string',
    'columns': "column or columns specified for the operation. The value can be either None or a list of strings: ['column1', 'column2', 'column3', ........]. Remember, x_axis and y_axis columns are also considered here."
}
default_parameters = {
    'dataframe_count': None,
    'dataframes': None,
    'between': None,
    'opted_operation': None,
    'x_axis': None,
    'y_axis': None,
    'data columns': None,
    'limits': None,
}

class Agent:
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
        sentiments = list(sentiment_dict.keys())
        template = f"""
          You are an AI assistant. Analyse the following text and classify it into the given sentiments.
          Text: {{text}}
          Sentiments:
          1. {sentiments[0]}: {sentiment_dict[sentiments[0]]}
          2. {sentiments[1]}: {sentiment_dict[sentiments[1]]}
          3. {sentiments[2]}: {sentiment_dict[sentiments[2]]}
          4. {sentiments[3]}: {sentiment_dict[sentiments[3]]}

          Example:
          After analysing the Text, return the sentiment. If the sentiment is matching two or more than two in the given, then return in a single python list like ['greetings', 'analyse', ......]  If sentiment doesn't match, return as 'None'. If the sentiment of a part of the text matches and other part didn't match, then return as [matches sentiment 1, 'None', matched sentiment 2, ...........]
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = message_
        response = chain.invoke({"text": human_message})
        return response.content

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
                return self.operation_analysis(message_=message_, sentiment_='analyse', params=params)
            else:
                reply = []
                for i in sentiment_:
                    if i is None:
                        reply.append("You caught me off-guard. Actually that query is out of my scope 😅. I can only assist you with data analysis. Apart from answering that, how else I can help you?")
                    if i == 'greetings':
                        reply.append('Hey, how can I help you? ')
                    elif i == 'status_based':
                        reply.append("I'm doing great. Thank you. What about you? Tell me, what can I do for you?")
                    elif i == 'end convo':
                        self.chat_status = 0
                        reply.append('Anytime to assist you 😊')
                return reply

    def operation_analysis(self,message_: str, sentiment_: str | list, params: dict | None = None):
        self.st_print('Entered operation_analysis')
        params = str(params).replace("{", "[")
        params = params.replace("}", "]")
        self.chat_status = 1
        template = f""""
          You are an AI assistant. Analyse the following text and return as directed:
          Text:{{text}}
          The user is asking to analyse a dataset.  The identified sentiment is {sentiment_} which means {sentiment_dict[sentiment_]}. You also given what are the details provided by the user so far in parameters (2nd in the references).
          Directions:
          Now, you need to update the values of parameters for the following:
          1. dataframe_count → Total number of dataframes (can be None or a natural number). Count if the name of the dataframe is mentioned. Otherwise don't count. For example, if the user says 'analyse a dataframe' or 'analyse a dataset', then he didn't give any names. If he gives 'analyse data.csv', where he included the name of the dataset/dataframe, then consider it.
          2. dataframes → Given Paths or names of the dataframes (can be None or a list: [path1, path2, ...] or [name1, name2, ...]). For example, if the user says 'analyse a dataframe' or 'analyse a dataset', then he didn't give any names. If he gives 'analyse data.csv', where he included the name of the dataset/dataframe, then consider it.
          3. opted_operation → Operation specified by the user (can be None or a list of dictionaries like [[operation1: [df1, df2, ...], columns:[column1, column2, .......], axis:[x_axis_column, y_axis_column]], [operation2: [df1, df2, ...], columns: None, axis: None]). opted_operation must be from the allowed operations list(mentioned in the 1st references), otherwise set to None, where, columns → Columns specified for the operation (can be None or a list of strings like ['column1', 'column2', 'column3', ...]), x_axis → Column name to be used on the x-axis (can be None or a string) and y_axis → Column name to be used on the y-axis (can be None or a string). Classify the columns mentioned in the 3rd reference 'Columns'.

          references:
          1. operation list: {operations}
          2. previous given parameters: {params}
          3. Columns: '''
    General Information Columns:
    • Date: The date when the data was recorded.
    • Time: The time of day when the data was recorded, likely in seconds or milliseconds since a reference point.
    •Id: Id of the row.

    Pressure-Related Columns (in Bar):
    • PT1(Bar) to PT12(Bar): These columns represent pressure measurements from various points in the system, possibly indicating pressures at different stages or components of the PTO system. The specific location of each pressure transducer (PT) would depend on the system's design.
    • PT21(Bar): Another pressure measurement, which might be a critical pressure point within the system.

    Displacement and Angle-Related Columns:
    • Zla1(mm), Zla2(mm), Zla3(mm): Vertical displacement measurements in millimeters, potentially from linear actuators or sensors monitoring vertical movement at different points.
    • theta1(deg), theta2(deg), theta3(deg): Angular measurements in degrees, likely representing rotational positions or orientations of components within the PTO system.

    Motion Reference Unit (MRU) Data (in degrees for rotations, meters for displacements):
    • Roll(deg): The rotational angle around the longitudinal axis (front to back), representing the side-to-side tilt.
    • Pitch(deg): The rotational angle around the transverse axis (side to side), representing the nose-up or nose-down tilt.
    • Yaw(deg): The rotational angle around the vertical axis, representing the heading or rotation in the horizontal plane.
    • Surge(m): The linear displacement along the longitudinal axis (forward/backward movement) in meters.
    • Sway(m): The linear displacement along the transverse axis (sideways movement) in meters.
    • Heave(m): The linear displacement along the vertical axis (up/down movement) in meters. Note that this column contains all null values in the provided sample.
          '''
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = message_
        response = chain.invoke({"text": human_message})
        json_struct = response.content.strip()

        # Remove Markdown fences if Gemini wrapped the JSON
        if json_struct.startswith("```"):
            json_struct = json_struct.strip("`")
            if json_struct.lower().startswith("json"):
                json_struct = json_struct[4:].strip()

        parameters_ = json.loads(json_struct)
        self.parameters = parameters_
        if parameters_:
            return self.requirement_handler(parameters_)
        else:
            return None

    def requirement_handler(self,params: dict | None = None):
        self.st_print('Entered requirement handler --------------------')
        requirements_ = []
        if params:
            if not params['opted_operation'] or len(params['opted_operation']) == 0:
                requirements_.append('opted_operation')
            else:
                if not params['dataframes'] or len(params['dataframes']) == 0:
                    requirements_.append('dataframes')
                operations_ = [list(x.keys())[0] for x in params['opted_operation']]
                if 'compare' in operations_:
                    if len(params['opted_operation'][operations_.index('compare')]['compare']['dataframes']) < 2:
                        requirements_.append('compare_dataframes')

                for x in operations_:
                    if x in ['min', 'max', 'dot-plot', 'bar-plot', 'box plot', 'pie chart', 'mean', 'median', 'mode']:
                        index_ = operations_.index(x)
                        if params['opted_operation'][index_][x]['columns'] is None or len(params['opted_operation'][index_][x]['columns']) == 0:
                            requirements_.append([f'{x}: "No columns"'])
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

    def req_llm(self,var, command: str):
        template = f"""
          You are an AI assistant, who generates only the answer to the asked questions and what mentioned is in the command.
          Command: {command}
          Variable: {var} 
          """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        human_message = self.message
        response = chain.invoke({"text": human_message})
        return response.content

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

    def implementor(self, message):
        bot_reply  = {'content' : [], 'type': ''}
        print('Implementor')
        self.message = message
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