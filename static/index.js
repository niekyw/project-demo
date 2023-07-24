// code adapted from https://codepen.io/cliff538/pen/GRYXqV

function getRandomColor() {
    var letters = "0123456789ABCDEF".split('');
    var color = "#";
    for (var i = 0; i < 6; i++) {
        color += letters[Math.round(Math.random() * 15)];
    }
    return color; 
}


var clickedTime; var createdTime; var reactionTime; 

function makeBox() {
    var time=Math.random();
    time=time*3000;
    
    setTimeout(function() {
        // generate a random number to determine whether to show a square or circle
        if (Math.random()>0.5) {
            document.getElementById("box").style.borderRadius="100px";
            } 
        else {
                document.getElementById("box").style.borderRadius="0";
            }
        
        // randomly generate object position
        var top= Math.random();
            top= top * window.innerHeight * 0.5;
        var left= Math.random();
            left= left * window.innerWidth * 0.8;

        // set object position and color            
        document.getElementById("box").style.top = top + "px";
        document.getElementById("box").style.left = left + "px"; 
        document.getElementById("box").style.backgroundColor=getRandomColor();
        document.getElementById("box").style.display="block";
        createdTime=Date.now();   
    }, time); 
}


// track clicks
var num_clicks = 0;

function startGame() {
    document.getElementById("start").onclick=function() {
        // change button color to show game started
        document.getElementById("start_game").style.backgroundColor = "rgb(0, 140, 255)";
        document.getElementById("start_game").innerHTML = "click on the shapes when they appear!";

        // calculate reaction time by setting createdTime when object is generated and clickedTime when object is clicked.
        const reactTimes = [];
        makeBox();
        document.getElementById("box").onclick=function() {
            clickedTime=Date.now();
            reactionTime=(clickedTime-createdTime)/1000;

            // save reaction time to a list
            reactTimes.push(reactionTime);

            // repeat code 5 5imes
            if (num_clicks < 4) {
                makeBox();
                num_clicks += 1
            }

            // after 5 times, make a post request through the HTML to pass the list of reaction times to python
            else {
                var form = document.getElementById("score")
                var input = document.getElementById("jsvar")
                input.value = reactTimes;
                form.submit();
                num_clicks = 0
            }
        }
    }
    
}







