/* Required Modules */
const {
    entersState,
    joinVoiceChannel,
    VoiceConnectionStatus,
    EndBehaviorType,
} = require("@discordjs/voice");
const {
    Client,
    Intents,
    MessageAttachment,
    Collection,
    REST,
    Routes,
    GatewayIntentBits,
} = require("discord.js");
const prism = require("prism-media");
const { createWriteStream } = require("node:fs");
const fs = require("fs");
// const ffmpeg = require("ffmpeg");
// const sleep = require("util").promisify(setTimeout);
const TOKEN =
    "MTI1Mzc1MDM5MTQxODUxOTY0Mw.GOl1Ym.LCcsLB49-Zwb6Eb2bxhuhjskBd8JMuTXY7r_P8";
const CLIENT_ID = "1253750391418519643";
const commands = [
    {
        name: "ping",
        description: "Replies with Ponggg!",
    },
    {
        name: "record",
        description: "Start recording your voice",
    },
    {
        name: "stop",
        description: "Stop recording your voice and leave the voice channel",
    },
];
const rest = new REST({ version: "10" }).setToken(TOKEN);
async function refreshCommands() {
    try {
        console.log("Started refreshing application (/) commands.");
        await rest.put(Routes.applicationCommands(CLIENT_ID), {
            body: commands,
        });
        console.log("Successfully reloaded application (/) commands.");
    } catch (error) {
        console.error(error);
    }
}
refreshCommands();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMessageReactions,
    ],
});

client.on("ready", () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on("interactionCreate", async (interaction) => {
    if (!interaction.isChatInputCommand()) return;
    const commands = interaction.commandName;
    console.log(commands);
    if (commands === "ping") {
        await interaction.reply("Pong!");
    } else if (commands === "record") {
        if (interaction.member.voice.channel) {
            const channel = interaction.member.voice.channel;
            const connection = joinVoiceChannel({
                channelId: channel.id,
                guildId: channel.guild.id,
                adapterCreator: channel.guild.voiceAdapterCreator,
            });
            try {
                await entersState(
                    connection,
                    VoiceConnectionStatus.Ready,
                    30e3
                );
                interaction.reply("Recording...");

                const receiver = connection.receiver;
                const userId = interaction.user.id;
                const audioStream = receiver.subscribe(userId, {
                    end: {
                        behavior: EndBehaviorType.AfterSilence,
                        duration: 1000,
                    },
                });

                const pcm = new prism.opus.Decoder({
                    rate: 16000,
                    channels: 2,
                    frameSize: 960,
                });
                const out = createWriteStream(`./recordings/${userId}.pcm`);

                audioStream.pipe(pcm).pipe(out);

                interaction.reply("Started recording!");
            } catch (error) {
                console.error(error);
                interaction.reply(
                    "Failed to join the voice channel or start recording."
                );
            }
        } else {
            interaction.reply("You need to join a voice channel first!");
        }
    } else if (commands === "stop") {
        if (interaction.member.voice.channel) {
            const channel = interaction.member.voice.channel;
            const connection = getVoiceConnection(channel.guild.id);
            if (connection) {
                connection.destroy();
                interaction.reply(
                    "Stopped recording and left the voice channel."
                );
            } else {
                interaction.reply("I'm not recording anything right now.");
            }
        } else {
            interaction.reply("You need to join a voice channel first!");
        }
    }
});

function getVoiceConnection(guildId) {
    return joinVoiceChannel.connections.get(guildId);
}

client.login(TOKEN);
