const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
    // Gérer les préflight CORS
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            body: ''
        };
    }

    try {
        console.log('Début du traitement de la requête:', event.path);
        
        // Exécuter le script Python
        const result = await runPythonScript(event);
        
        console.log('Résultat Python:', result);
        
        return {
            statusCode: result.statusCode || 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify(result.body)
        };
    } catch (error) {
        console.error('Erreur:', error);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({ error: error.message })
        };
    }
};

function runPythonScript(event) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [
            path.join(process.cwd(), 'backend', 'netlify_handler.py'),
            JSON.stringify(event)
        ]);

        let result = '';
        let errorOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
            console.log('Python stdout:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
            console.error('Python stderr:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            console.log('Processus Python terminé avec code:', code);
            console.log('Résultat complet:', result);
            
            if (code !== 0) {
                reject(new Error(`Python script failed: ${errorOutput}`));
            } else {
                try {
                    const parsedResult = JSON.parse(result);
                    resolve(parsedResult);
                } catch (e) {
                    // Si le résultat n'est pas du JSON, le retourner tel quel
                    resolve({
                        statusCode: 200,
                        body: result
                    });
                }
            }
        });
    });
}