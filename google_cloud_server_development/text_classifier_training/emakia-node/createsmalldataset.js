const fs = require('fs');
const path = require('path');

async function divideFileIntoChunks(inputFilePath, chunkSize) {
    try {
        const fileNameWithoutExtension = path.parse(inputFilePath).name;
        const fileStream = fs.createReadStream(inputFilePath);
        let lineNumber = 0;
        let chunkNumber = 1;
        let currentChunk = [];
        let header = null; // Variable to store the header

        const rl = require('readline').createInterface({
            input: fileStream,
            crlfDelay: Infinity,
        });

        // Extract the header
        header = (await rl[Symbol.asyncIterator]().next()).value.split(',');
        
        for await (const line of rl) {
            currentChunk.push(line);https://github.com/Emakia-Project/emakia/blob/main/createsmalldataset.js
            lineNumber++;

            if (lineNumber % chunkSize === 0) {
                const chunkFileName = `${fileNameWithoutExtension}-${chunkNumber}.csv`;
                // Write the header to the chunk file
                fs.writeFileSync(chunkFileName, header.join(',') + '\n');
                // Write the chunk data to the chunk file
                fs.appendFileSync(chunkFileName, currentChunk.join('\n'));
                console.log(`Chunk ${chunkNumber} written with ${chunkSize} lines.`);
                currentChunk = [];
                chunkNumber++;
            }
        }

        // Write the remaining lines to a new file
        if (currentChunk.length > 0) {
            const chunkFileName = `${fileNameWithoutExtension}-${chunkNumber}.csv`;
            // Write the header to the chunk file
            fs.writeFileSync(chunkFileName, header.join(',') + '\n');
            // Write the remaining chunk data to the chunk file
            fs.appendFileSync(chunkFileName, currentChunk.join('\n'));
            console.log(`Chunk ${chunkNumber} written with ${currentChunk.length} lines.`);
        }

        console.log(`File divided into ${chunkNumber} chunks.`);
    } catch (error) {
        console.error('Error dividing file into chunks:', error);
    }
}

// Usage example
const inputFilePath = 'tweets-labels-processed.csv'; // Replace with the path to your input file
const chunkSize = 3000;
divideFileIntoChunks(inputFilePath, chunkSize);
