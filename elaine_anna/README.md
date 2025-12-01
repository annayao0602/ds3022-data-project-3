# DS3022 Data Project 3

**Names:** Elaine Liu, Anna Yao

**Data Source:** NumPy GitHub Repository

**Overview:** This repository ingests the full hisory of commits from the NumPy GitHub repository using Kafka and stores the data in DuckDB for further analysis. This information is visualized using a GUI application/dashboard that summarizes key information such as the number of commits over time and top contributors for users. 

**Challenges:**
- One challenge we faced was being able to get a substantial amount of data ~50K-100K. There aren't a ton of repositories with that many records, and we ended up choosing the NumPy GitHub repo because it had ~40K commits. We figured this quantity of data would be substantial enough and our application could be applied to larger repos in the future just by changing the repo name variable. To process the data, we created a producer to take data from the github repo, send it to Kafka, and created a consumer to read from it. To store the data and do analysis, we used a DuckDB database.
- Another challenge we faced was choosing what visualizations we wanted to include in our GUI application. Because we had so much data on hand, there were a lot of possibilities, such as commits over time, forks over time, commit key words, top contributors, number of stars, etc. We ended up choosing to visualize commits over time and top contributors overall, as we thought it would be the most useful information for a new user. If we were to continue this project, some additional features could be to let the user choose a github repository and generate a dashboard based on the input. 

**Analysis:**
![2](https://github.com/user-attachments/assets/31d63ff3-5bb5-4983-aea0-2445febbf84f)

![1](https://github.com/user-attachments/assets/965cb958-de74-4fd2-a0fe-22e9dd698a6d)

We can see that there are 40,137 total commits, which shows that NumPy is a pretty long standing and well developed package in the Python ecosystem. Based on the commit time series graph, we see that it was first released in around 2003 and has been continually updated since then. 
- The line plot has an upward trend, meaning that on average, the number of commits per month has increased. We can see that the most significant peak is at around 2006, which was its official release. There is a slight dip at around 2022-2023, which could indicate developers were working on different projects/packages. Since we don't see a decline in the number of commits over time, we can assume that NumPy will not depreciate and will continue to be a popular and widely-loved Python package. 
- Based on the top contributors bar chart, we see that Charles Harris is the overall top contributor with 7060 commits. This is quite significant, considering the second top contributor only has 2806 commits. This makes sense, since he is the NumPy release manager and has worked on its predecessor packages. 

Link: https://github.com/elaineliu05/dp3-coderepo
