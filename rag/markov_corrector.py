from collections import defaultdict


class MarkovCorrector:

    def __init__(self, texts):

        self.transitions = defaultdict(lambda: defaultdict(int))

        for text in texts:
            words = text.lower().split()

            for i in range(len(words) - 1):
                w1 = words[i]
                w2 = words[i + 1]

                self.transitions[w1][w2] += 1


    def correct(self, query):

        words = query.lower().split()

        corrected = []

        for i, w in enumerate(words):

            if i == 0:
                corrected.append(w)
                continue

            prev = corrected[-1]

            if prev in self.transitions:

                candidates = self.transitions[prev]

                best = max(candidates, key=candidates.get)

                if w not in candidates:
                    corrected.append(best)
                else:
                    corrected.append(w)

            else:
                corrected.append(w)

        return " ".join(corrected)