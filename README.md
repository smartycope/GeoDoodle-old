# GeoDoodle
GeoDoodle is a graph paper-like doodle program. I really like doodling on graph paper, making cool repeating patterns so I decided to automate it. It allows you to create cool patterns using various tools and features I've added. You can also load, save, or export your pattern. It is not, however, just a regular drawing program. All lines are intended to line up with the dots, or other lines.

## Installation
It's written in modern Python using PyQt6 (never could get pyside to work for me).
```
git clone https://github.com/smartycope/GeoDoodle.git
cd GeoDoodle
pip install -r requirements.txt
```

## History
This has been my personal cutting edge project; I keep rewriting it as I learn new things. That's why there's so many old versions included. They're old and gross, but I spent so much time on them to just delete them.

I first wrote it in C++ on top of a garbage freeglut API given to me, because it was my first semester of college and I was excited about this cool idea that I had and I could actually do it. Freeglut was what my assignments that semester used, so I just hacked that code, not really knowing what I was doing. Someone really needs to write new assignments for that class.

I then came back to the project about a year later, after starting many other projects, and knowing way, way more. I also had discovered Python. I ended up scrapping the entire codebase and rewriting the entire thing from scratch in Python (using pygame) and got it roughtly to where it was before, in about 4 hours. It was pretty cool. I then added a bunch more features and made everything a lot nicer (pygame is an excellent API), including adding menus and options and a better repeating system. I eventually got stymied by the GUI's though. At that point I hadn't really done much with GUI's, and tried using pygame-gui, which isn't a bad API, it's just really not meant for what I wanted, and ended up writing huge, very nasty wrappers around their classes and it just wasn't worth it.

A couple months later, I had the idea to use Qt. It was something I'd wanted to learn for a while, but I never really had a project suited to it, until I realized this was perfect. Turns out, Qt is **fantastic**. There's a reason it's so popular. It definitely takes getting used to, but it's all very clean, and QtCreator is super handy. Using Qt allowed me to expand even further, and add more features far more intuitively.

A few months after *that*, I took a linear algebra course and had the realization that a bunch of the problems I had with repeating patterns and keeping track of coordinates could all be solved by using matrices for coordinates and multiplying by a transformation matrix. I then rewrote the whole codebase (*again*) to use numpy to represent dots and lines instead. That solved a *ton* of conceptual problems, and allowed me to add a bunch of features like mirroring and rotating and scaling. It also cleaned a the code a ton too. 

It's been a while since I've last touched this project, and it's due for another rewrite at some point. I've learned a ton more since the last rewrite, and I remember I left it with a few largeish bugs. I also didn't know how to use git very well back then (I do now), so proper branching and commits would help a bunch. I have a vauge idea of integrating a bunch of other libraries, like polars (polars is *fast*), shapely, and a couple others. Also, moving away from Qt might be nice too, but I don't know what to move to.
