# Spec

- A web form accepts one or more genome IDs.
- The `VectorSearch` python script is called with the given IDs.
  - The `VectorSearch` script loads the genome .csv files for the given species.
  - The `VectorSearch` script returns a csv file
- The csv results of the script are available for download.
- The csv results are visualized via chart.
  - The chart is off-the-shelf, as seen on https://plasmodb.org/plasmo/app/

## Budget

Project budget is approximately 50,000 SEK, which maps to ~62 billable hours, or 14 [billable work chunks](https://nikolas.ws/project-managing-conceptual-labor). If this were a freelance project I would be aiming to get it done in [6 billable work chunks](https://nikolas.ws/project-managing-conceptual-labor#schedule).

## Schedule

### 6-Blob Schedule

1. Initial application setup, CI/CD pipelines, and stubbed UX flow.
2. Integrate the `VectorSearch` python script with i/o.
3. Tighten up visual design of the user experience.
4. Overflow Buffer Blob
5. Integrate the genome CSV visualizer.
6. Adjust UX to enable batch search and download.

### 14-Blob Schedule

1. Initial applications setup, CI/CD pipeline
2. Stubbed UX and appliation flow
3. Integrate the `VectorSearch` python script
4. Ensure correct function signtite i/o
5. Visual design of user experience.
6. Wrap up the design of the user experience.
7. Overflow buffer blob
8. Overflow buffer blob
9. Overflow buffer blob
10. Start integrating genome visualizer.
11. Finish the genome visualizer.
12. Adjust the user experience to allow multiple in/out.
13. Finalize the user experience for batch downloading.
14. Final wiggle all the knobs and dials.

## Questions

When writing the Reverse Complement HR1 and HR2 from the source `fasta` files, does that process need to run on each request, or can we run that once and commit the reverse compliment files into the codebase?

Can you help me understand the function signature of the program? Right now it looks like it doesn't accept any parameters, and returns a CSV for each of the predefined `Carina_Genes`. What should our user input be? Is there a list of acceptable inputs?

What is the visualization tool called? Where does that code live?