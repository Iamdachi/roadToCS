# roadToCS
#### Video Demo:  https://youtu.be/vMtgPydeeBA
#### Description:

##### About Project
A lot of people have imposter syndrome about their work or their studies in CS. Traditionally, a good way to become confident in your skills was to go to a great university. However, getting into a prestigeous university is tough and expensive. So, many people are left wondering: Are they learning enough? and what should they be learning in the first place?

Luckily for us the best universities have made their learning material available for free. However, going through them is still daunting... You do not know which courses to take, what lectures are offered in those courses, which ones to do first and so on... 

I have compiled a road-map of academic CS curriculum. This list is mostly based on universities like MIT, Stanford, Harvard, and etc. This roadmap contains roughly all the "requirements" that students need to go through during their Bachelors Degree studies. So, at the end of it you should really have fundamental CS knowledge.

Keep in mind, those universities try to give you a fundamental problem solving skills and understanding of core principles. Even though CS field is progressing very rapidly, underlying "first principles" do not change that fast in the computer science and mathematics. For example, a Calculus class from MIT from 2010 will still be relevant to you if you wish to learn Calculus itself. 

P.S. The road-map itself requires no prerequisite knowledge in programming/coding. Some math might be needed for calculus though, which is an introductory course in many universities. I imagine if you visit this website, you already have this kind of knowledge, or can learn it easily. If needed simply try to search high-school level mathematics...

I designed this website in the simillar spirit to neetcode.io, where you can see the roadmap, each points/nodes on the road contain many problem explanation videos and you can save your progress.

##### How I built it
As I mentioned, I wanted to build an app in the spirit of neetcode.io. I wanted to have a graphical tree of this roadmap, where each node in the tree is a university course, and inside each course there is a lecture list. Added an ability for users to save their progress of each learned lecture.

Front end of this web application is the most important I think. I wanted the graph to be well put together and elegant (like neetcode). I personally do not consider myself a front-end developer so I did not want to waste time on big frameworks like Angular. So, I used plain javascript with D3 library for graph visualizations. D3 draws rectangles, lines, texts and all the right "ingredients" for the optics of the roadmap. It fetches course and lecture information from back-end server. Information is organized into JSON files. One file contains info about drawing rectangles, with university course names and position coordinates on the screen. Another JSON file, organizes lectures for each course, including lecture names and youtube links. With this information the whole roadmap is drwan. Once a course in the tree is clicked a sidebar appears, containing all the lectures for that course. User can save their progress if they sign up. Otherwise, their progress will be lost. Huge inspiration for this project came from neetcode.io. So, thanks to him! He also made a video on his channel where he tried to make AI build the similar website. The AI failed miserably and I am a little proud for being a little better than AI so far...

Back End of this application runs on Flask. I wanted to keep the back end simple and I think it is. The back-end python code is way more simplistic and less complicated than the JS code that draws the roadmap. First features that I built for this website was to add Google Authentication. Actually, I purposefully did not implement the authentication feature myself, as I have previously done it in CS50 finance project. However, I was really interested in how other apps handle Google Authentication. So, I built it in. For that I used Google Cloud Console and read a documentation. Turns out you just need to do some additional authentication handling and that's it. I think this is an easier and safer way to authenticate people and everyone has a Gmail account these days. In the future I might add Github Authentication as well.. 

Other than that this is a normal flask application. It has many routes. They render the roadmap page for the logged in user a little differently. I built my database on sqlite. I have three tables roughly. Users, Course, Lectures. and I have many to many relationships to Users and Lectures, which saves the lectures that the user has done. When a user logs in his account a database command is made that selects all the lectures he has done. Then a JSON file is modified, to be sent to the frontend to render the roadmap with progress bars. I use GUnicornd and NGIX to hook up the local app to the global domain name.

I bought the domain on GoDaddy and hosted my app on DigitalOcean. You can visit the app on roadtocs.com.

That is pretty much it. Technology Stack used was: JS(D3 Library), Python(Flask), SQL(sqlite).
