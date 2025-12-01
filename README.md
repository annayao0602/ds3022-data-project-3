# DS3022 Data Project 3

Names: Elaine Liu, Anna Yao

Data Source: NumPy GitHub Repository

Overview: This repository ingests the full hisory of commits for the NumPy GitHub repository using Kafka and stores the data in DuckDB for further analysis. This information is visualized using a GUI application/dashboard that summarizes key information such as the number of commits over time and top contributors for users. 

Challenges: 
- One challenge we faced was being able to get a substantial amount of data ~50K-100K. There aren't a ton of repositories with that many records, and we ended up choosing the NumPy GitHub repo because it had ~40K commits. We figured this quantity of data would be substantial enough and our application could be applied to larger repos in the future. To process the data, we created a  producer to take data from the github repo, send it to Kafka, and created a consumer to read from it. To store the data and do analysis, we used a DuckDB database.
- Another challenge we faced was choosing what visualizations we wanted to include in our GUI application. Because we had so much data on hand, there were a lot of possibilities, such as commits over time, forks over time, commit key words, top contributors, number of stars, etc. We ended up choosing to visualize commits over time and top contributors overall, as we thought it would be the most useful information for a new user. If we were to continue this project, some additional features could be to let the user choose a github repository and generate a dashboard based on the input. 

Analysis:


Link: https://github.com/annayao0602/ds3022-data-project-3

- Overall cohesiveness, originality, and focus of the project (5 points)

## Judging & Prizes 🏆
After completion students and TAs will vote for their top 3 projects and there will be a prize for the top voted project in each section. (And I mean a _real_ prize.)

