// netlify/functions/api/api.js - Version simplifiée pour test
exports.handler = async (event, context) => {
    console.log('🚀 Fonction appelée:', event.path);
    
    // Headers CORS
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    };

    // Gérer les préflight CORS
    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    // Routes de l'API
    if (event.path === '/api/villes' && event.httpMethod === 'GET') {
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ 
                villes: ['Douala', 'Yaounde'],
                message: 'API fonctionne!'
            })
        };
    }

    if (event.path === '/api/communes' && event.httpMethod === 'GET') {
        const ville = event.queryStringParameters?.ville || '';
        let communes = [];
        
        if (ville.toLowerCase().includes('douala')) {
            communes = ['Douala 1', 'Douala 2', 'Douala 3', 'Douala 4', 'Douala 5'];
        } else if (ville.toLowerCase().includes('yaounde')) {
            communes = ['Yaounde 1', 'Yaounde 2', 'Yaounde 3', 'Yaounde 4', 'Yaounde 5', 'Yaounde 6', 'Yaounde 7'];
        }
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(communes)
        };
    }

    // Route non trouvée
    return {
        statusCode: 404,
        headers,
        body: JSON.stringify({ error: 'Route non trouvée: ' + event.path })
    };
};
