def operation_analysis(self, message_: str, params: dict | None = None):
    self.st_print('Entered operation_analysis')
    # llm = OllamaLLM(model = 'gemma3:4b', temperature = 0)
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-pro', temperature=0)
    self.chat_status = 1
    template = """
      You are an AI assistant. Analyse the following text and return as directed:
      Text: {text}
      The user is asking to analyse a dataset. You also given what are the details provided by the user so far (2nd in the references).

      Directions:
      Now, you need to update the values of {parameters} for the following and return the values as {parameter_structure}:
      {parameter_definition}

      references:
      1. operation list: {operations}
      2. previous given parameters: {params}
      Note: Updating means replacing old values only if the user asks to. Otherwise add the new values to the previous. Carefully analyse.
      """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    human_message = message_
    response = chain.invoke(
        {"text": human_message, "operations": operations, "params": params, "parameters": self.parameters,
         "parameter_definition": parameter_definition, "parameter_structure": parameter_structure})
    json_struct = None
    if response:
        if isinstance(response, str):
            json_struct = response.strip().removeprefix("```json").removesuffix("```").strip()
            json_struct = repair_json(json_struct)

        parameters_ = json.loads(json_struct)
        if parameters_:
            self.parameters = parameters_
            return self.requirement_handler(parameters_)
        else:
            return None














