const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, 'public');
const outputFile = path.join(publicDir, 'file-list.json');

function walkAndFilterCSV(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      results = results.concat(walkAndFilterCSV(filePath));
    } else if (file.toLowerCase().endsWith('.csv')) {
      results.push(path.relative(publicDir, filePath).replace(/\\/g, '/'));
    }
  });
  return results;
}

function generate() {
  const csvFiles = walkAndFilterCSV(publicDir);
  fs.writeFileSync(outputFile, JSON.stringify(csvFiles, null, 2), 'utf-8');
  console.log(`[${new Date().toLocaleTimeString()}] ✅ CSV file list updated with ${csvFiles.length} file(s).`);
}

generate(); // Run once at startup

// Optional: re-run every 60 seconds --> Page will refresh
setInterval(generate, 60000); // unit in ms
