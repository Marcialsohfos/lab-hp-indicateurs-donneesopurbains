// netlify/functions/api.js
exports.handler = async (event, context) => {
    console.log('📍 Fonction appelée:', event.path, event.httpMethod);
    
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    };

    // CORS preflight
    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    // Routes
    if (event.path === '/api/villes') {
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(['Douala', 'Yaounde'])
        };
    }

    if (event.path === '/api/communes') {
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

    if (event.path === '/api/indicateurs') {
        const commune = event.queryStringParameters?.commune || '';
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                commune: commune,
                ville: 'Yaounde',
                message: 'Données de test pour ' + commune,
                troncons_voirie: [],
                quartiers_taudis: []
            })
        };
    }

    return {
        statusCode: 404,
        headers,
        body: JSON.stringify({ error: 'Route non trouvée: ' + event.path })
    };
};