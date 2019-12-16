const Discord = require('discord.js');
const client = new Discord.Client();
const auth = require('./auth.json');

let rolls = [];
let pattern = new RegExp("@.+rolled\\s(\\d+.)");

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});


client.on('message', msg => {

    //console.log(pattern.test(msg.content));

    if (pattern.test(msg.content)) {
        let roll = pattern.exec(msg.content)[1]
        msg.reply(roll);
    }
});

/*
client.on('message', function (user, userID, channelID, message, evt) {
    // Our bot needs to know if it will execute a command
    // It will listen for messages that will start with `!`
    if (message.substring(0, 1) == '!') {
        var args = message.substring(1).split(' ');
        var cmd = args[0];
       
        args = args.splice(1);
        switch(cmd) {
            // !ping
            case 'ping':
                bot.sendMessage({
                    to: channelID,
                    message: 'Pong!'
                });
            break;
            // Just add any case commands if you want to..
         }
     }
});
*/

  client.login(auth.token);