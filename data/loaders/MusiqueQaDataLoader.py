import json
import os
import tqdm
from constants import Split
from data.datastructures.answer import Answer
from data.datastructures.dataset import DprDataset
from data.datastructures.evidence import Evidence
from data.datastructures.question import Question
from data.datastructures.sample import Sample
from data.loaders.BasedataLoader import GenericDataLoader


class MusiqueQADataLoader(GenericDataLoader):
    def __init__(self, dataset: str, tokenizer="bert-base-uncased", config_path='test_config.ini', split=Split.TRAIN,
                 batch_size=None):
        self.titles = [self.corpus[idx]["title"].split(" - ")[0] for idx in list(self.corpus.keys())]
        print(self.titles[100],self.corpus["100"])
        super().__init__(dataset, tokenizer, config_path, split, batch_size)


    def load_raw_dataset(self, split=Split.TRAIN):
        dataset = self.load_json(split)
        print(len(dataset))
        for  query_index, data in enumerate(tqdm.tqdm(dataset)):
            if len(data["paragraphs"]) == 0:
                data["paragraphs"] = ['some random title', ['some random stuff']]
            for evidence_set in data["paragraphs"]:
                title = evidence_set["title"]
                #for evidence in evidence_set[1]:
                evidence = evidence_set["paragraph_text"]
                #print(list(self.titles).index(title.split(" - ")[0]))
                self.raw_data.append(
                    Sample(query_index, Question(data["question"]), Answer(data["answer"]),
                            Evidence(evidence, 
                                    list(self.titles).index(title.split(" - ")[0]))
                ))


    def load_tokenized(self):
        if self.tokenized_path and os.path.exists(self.tokenized_path):
            self.logger.info("Loading DPR data from {}".format(self.tokenized_path))
            with open(self.tokenized_path, "r") as f:
                ip_ids, ip_attention, evidence_ids, evidence_attention = json.load(f)
        else:
            ip_ids, ip_attention = self.tokenize_questions()
            evidence_ids, evidence_attention = self.tokenize_evidences()
        return DprDataset(ip_ids, ip_attention, evidence_ids, evidence_attention)