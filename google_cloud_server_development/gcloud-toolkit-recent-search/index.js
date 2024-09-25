const express = require('express');
const bodyParser = require('body-parser')
const cors = require('cors')
const search = require('./controllers/search')
const winston = require('winston');
//const { LoggingWinston } = require('@google-cloud/logging-winston');





// Create a Winston logger and add the Cloud Logging transport
//const loggingWinston = new LoggingWinston();


/*const logger = winston.createLogger({
    projectId: 'webhemakia',
    level: "info",
    format: winston.format.json(),
    format: combine(timestamp(), json()),
    transports: [
      new winston.transports.Console(),
      new winston.transports.File({ filename: 'combined.log' }), 
      loggingWinston
    ]
  }); */

// Create a middleware that will use the provided logger.
// A Cloud Logging transport will be created automatically
// and added onto the provided logger.
//const mw = await loggingWinston.express.makeMiddleware(logger);

const app = express();
const port = process.env.PORT || 4050;
//app.use(loggingWinston);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use(cors());
app.options('*', cors()) 
app.post('*', cors()) 
app.use('/search',search);
//app.use(mw);

app.listen(port, ()=>   {
    console.log("App listening on port",port)
})