from rapidfuzz import fuzz


class Evaluator:
    def __init__(self, source_json):
        self.source = source_json
        self.abnormals = [
            i["test"]
            for i in self.source["labs_json"]
            if i["status"] in ["abnormal", "abn", "critical"]
        ]
        # self.diseases = [
        #     i[""]
        # ]

    def calculate_lab_recall(self, summary_text):
        """
        Custom algorithm to check if abnormal and critical labs were mentioned in summary
        """
        try:
            recall = [
                1 for word in self.abnormals if fuzz.partial_ratio(word, summary_text) > 80
            ]
            print(len(recall), len(self.abnormals), self.abnormals)
            return len(recall) / len(self.abnormals)
        except Exception as e:
            print(e)
            raise

    def llm_judge(self, summary_text):
        pass

test_results = []



# evaluator = Evaluator(ex_res)
# print(
#     evaluator.calculate_lab_recall(
#         "Chest X-Ray The patient has a confirmed positive sputum culture for Staphylococcus aureus and shows typical abnormal findings of pneumonia on chest X-ray. The complete blood count results are within normal limits."
#     )
# )
