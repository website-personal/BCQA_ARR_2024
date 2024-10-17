from dexter.llms.llm_engine_orchestrator import LLMEngineOrchestrator
import json
import pandas as pd
from dexter.config.constants import Split
from dexter.data.loaders.RetrieverDataset import RetrieverDataset


if __name__=="__main__":
        config_instance = LLMEngineOrchestrator()
        llm_instance = config_instance.get_llm_engine(data="",llm_class="openai",model_name="gpt-3.5-turbo")
        #assertTrue(isinstance(llm_instance, OpenAIEngine))
        with open("musique_colbert_docs.json") as f:
                evidence = json.load(f)
        question_df = {"questions":[],"answers":[]}


        loader = RetrieverDataset("strategyqa","strategyqa-corpus",
                               "evaluation/config.ini", Split.DEV,tokenizer=None)        
        queries, qrels, corpus = loader.qrels()
        raw_data = loader.base_dataset.raw_data
        system_prompt = "Following the given examples, Given the question think step by step  and output final answer for the question as one of true or false preceded by  [Final Answer]: \n"
        matches = 0
        mismatches = 0
        ids = []
        for row in raw_data:
                if row.question.id() in ids:
                        continue
                else:
                        ids.append(row.question.id())
                user_prompt = """
                                      [Original Question]: Are any animals in Chinese calendar Chordata?
                      [Final Answer]: true \n\n
                                            [Original Question]: Does Andrew Johnson's presidential number exceed Elagabalus's Emperor number?,
                      [Final Answer]: False \n\n 
                 [Original Question]: Are more people today related to Genghis Khan than Julius Caesar?,
                      [Final Answer]: True \n\n 

                [Original Question]: Will the Albany in Georgia reach a hundred thousand occupants before the one in New York?,
                      [Final Answer]: False \n\n 

         [Original Question]: Would an uninsured person be more likely than an insured person to decline a CT scan?,
                      [Final Answer]: True \n\n 
                Following above examples, Think step by step and give  answer preceded by [Final Answer]: the Question:"""+row.question.text()
                print("user_prompt",user_prompt)
                chain_answer = llm_instance.get_chat_completion(user_prompt,system_prompt)
                if "not possible" in chain_answer.lower():
                        mismatches+=1
                        continue
                elif "unknown" in chain_answer.lower():
                        mismatches+=1
                        continue
                elif len(chain_answer.split("[Final Answer]:")) >1:
                        answer = chain_answer.split("[Final Answer]:")[-1]
                        print("************",answer,row.answer.text())
                        if str(row.answer.text()).lower() in answer.lower():
                                matches+=1
                        else:
                                mismatches+=1
                else:
                        mismatches+=1
                question_df["answers"].append(chain_answer)
                question_df["questions"].append(str(row.question.text()))


                final_questions = pd.DataFrame(question_df)
                print("EM", matches/(matches+mismatches))
                print(final_questions)
                final_questions.to_csv("chatgpt_strategy_few_shot.tsv",sep="\t",index=False)


