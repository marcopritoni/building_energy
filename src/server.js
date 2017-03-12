var http = require("http");
var fs = require("fs");
var express = require("express");
var events = require("events");
var url = require("url");
var PythonShell = require('python-shell');
var options = {
  mode: 'text',
  pythonPath: 'C:/Users/zeusa/Anaconda2/python',
  pythonOptions: ['-u','-W ignore'] 
};
var app = express();
app.use(express.static('web interface demo v1'));

app.get('/', function(req, res){
  res.sendFile(__dirname + "/../" + "web interface demo v1/index.html");
});

app.get('/python.json', function(req, res){
  PythonShell.run('mv_model_main.py', options, function(err, results) {
  	console.log(err);
  	console.log("results are " + results);
    res.json(results);
  });
});

app.listen(8080);

console.log('Server running at http://127.0.0.1:8080');