#!/usr/bin/env python
# coding: utf-8

# In[18]:


import joblib
import pandas as pd


model = joblib.load(
    "D:/Projects-Practice-Freelance/Customer-Compliant-AI/ml/models/best_model.pkl"
)

preprocessor = joblib.load(
    "D:/Projects-Practice-Freelance/Customer-Compliant-AI/ml/models/preprocessor.pkl"
)


def predict_dispute_risk(
    complaint_text
):

    try:

        sample = {

            #"Complaint ID": "TEST-001",

            "Complaint ID": 1,

            "Product": "Unknown",

            "Sub-product": "Unknown",

            "Issue": "Unknown",

            "Sub-issue": "Unknown",

            "Company": "Unknown",

            "State": "CA",

            #"ZIP code": "00000",

            "ZIP code": 0,

            "Submitted via": "Web",

            "Company response to consumer": "Unknown",

            "Company public response": "Unknown",

            "Tags": "Unknown",

            "Consumer consent provided?": "Consent provided",

            "Timely response?": "Yes",

            "Date sent to company": "2026-07-20",

            "Consumer complaint narrative":
                complaint_text,

            "Narrative Available": 1,

            "Narrative Length":
                len(complaint_text),

            "Word Count":
                len(
                    complaint_text.split()
                ),

            "Average Word Length":
                len(complaint_text)
                /
                max(
                    len(
                        complaint_text.split()
                    ),
                    1
                ),

            "Received Year": 2026,

            "Received Month": 7,

            "Received Quarter": 3,

            "Received Day": 20,

            "Received Weekday": 0

        }

        df = pd.DataFrame(
            [sample]
        )

        processed = preprocessor.transform(
            df
        )

        prediction = model.predict(
            processed
        )[0]

        return str(
            prediction
        )

    except Exception as e:

        print(
            "ML Prediction Error:",
            e
        )

        return "Unknown"


# In[19]:


print(
    preprocessor.feature_names_in_
)


# In[20]:


preprocessor.feature_names_in_


# In[21]:


print(
    predict_dispute_risk(
        """
        I have repeatedly contacted customer
        support regarding unauthorized charges
        on my credit card and no action has
        been taken.
        """
    )
)


# In[ ]:




