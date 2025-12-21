// Configuration des onglets disponibles
 const TABS_CONFIG = {
    // Onglets pour tous les invités
    common: [
        {
            id: 'ordre_jour',
            title: 'Ordre du jour',
            icon: '📅',
            description: 'Programme de la journée',
            page: 'ordre_jour.html'
        },
        {
            id: 'menu',
            title: 'Menu',
            icon: '🍽️',
            description: 'Découvrez les délices du jour',
            page: 'menu.html'
        },
        {
            id: 'ma_table',
            title: 'Ma table',
            icon: '🪑',
            description: 'Votre plan de table',
            page: 'ma_table.html'
        },
        {
            id: 'media',
            title: 'Média',
            icon: '📸',
            description: 'Photos et vidéos partagées',
            page: 'media.html'
        },
        {
            id: 'info',
            title: 'Infos',
            icon: 'ℹ️',
            description: 'Informations pratiques',
            page: 'info.html'
        }
    ],
    // Onglets pour les administrateurs
    admin: [
        {
            id: 'ordre_jour',
            title: 'Ordre du jour',
            icon: '📅',
            description: 'Programme de la journée',
            page: 'ordre_jour.html'
        },
        {
            id: 'menu',
            title: 'Menu',
            icon: '🍽️',
            description: 'Découvrez les délices du jour',
            page: 'menu.html'
        },
        {
            id: 'vue_generale_salle',
            title: 'Vue générale de la salle',
            icon: '🏛️',
            description: 'Vue d\'ensemble de la salle',
            page: 'vue_generale_salle.html',
            badge: 'ADMIN'
        },
        {
            id: 'vue_entree',
            title: 'Vue de l\'entrée',
            icon: '🚪',
            description: 'Surveillance de l\'entrée',
            page: 'vue_entree.html',
            badge: 'ADMIN'
        },
        {
            id: 'info_admin',
            title: 'Info admin',
            icon: '⚙️',
            description: 'Gestion des informations',
            page: 'info_admin.html',
            badge: 'ADMIN'
        },
        {
            id: 'media_admin',
            title: 'Média admin',
            icon: '📹',
            description: 'Gestion des médias',
            page: 'media_admin.html',
            badge: 'ADMIN'
        }
    ]
};

async function loadUsers() {
    try {
        const response = await fetch('utilisateur.json', {
            cache: "no-store" // évite les problèmes de cache en développement
        });

        if (!response.ok) {
            throw new Error("Impossible de charger utilisateur.json");
        }

        return await response.json();
    } catch (error) {
        console.error(error);
        document.body.innerHTML = "<h2>Erreur de chargement des données</h2>";
        return null;
    }
}

// Base de données simulée des utilisateurs (À REMPLACER PAR FIREBASE)
const USERS_DB = await loadUsers();

// Fonction pour extraire le token depuis l'URL
function getTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('token');
}

// Fonction pour valider et récupérer le profil utilisateur
function authenticateUser(token) {
    // Simulation de validation (À REMPLACER PAR APPEL FIREBASE)
    if (USERS_DB[token]) {
        return {
            success: true,
            user: USERS_DB[token]
        };
    }
    return {
        success: false,
        error: 'QR Code invalide ou expiré'
    };
}

// Fonction pour générer les onglets selon le profil
function generateTabs(userRole) {
    const tabs = [...TABS_CONFIG.common];
    
    if (userRole === 'admin') {
        tabs.push(...TABS_CONFIG.admin);
    }
    
    return tabs;
}

// Fonction pour afficher les onglets
function renderTabs(tabs) {
    const navContainer = document.getElementById('navigation');
    navContainer.innerHTML = '';
    
    tabs.forEach(tab => {
        const tabCard = document.createElement('a');
        tabCard.className = 'tab-card';
        tabCard.href = tab.page;
        
        tabCard.innerHTML = `
            <div class="tab-icon">${tab.icon}</div>
            <h3>${tab.title}</h3>
            <p>${tab.description}</p>
            ${tab.badge ? `<span class="admin-badge">${tab.badge}</span>` : ''}
        `;
        
        navContainer.appendChild(tabCard);
    });
    
    navContainer.style.display = 'grid';
}

// Fonction pour afficher une erreur
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('loading').style.display = 'none';
}

// Initialisation de l'application
async function initApp() {
    try {
        // Étape 1 : Récupérer le token
        const token = getTokenFromURL();
        
        if (!token) {
            showError('❌ Aucun QR code détecté. Veuillez scanner votre invitation.');
            return;
        }
        
        // Étape 2 : Authentifier l'utilisateur
        const authResult = authenticateUser(token);
        
        if (!authResult.success) {
            showError('❌ ' + authResult.error);
            return;
        }
        
        const user = authResult.user;
        
        // Étape 3 : Sauvegarder la session
        sessionStorage.setItem('currentUser', JSON.stringify(user));
        sessionStorage.setItem('authToken', token);
                
        // Étape 4 : Afficher le message de bienvenue
        document.getElementById('userName').textContent = user.name;
        document.getElementById('welcome').style.display = 'block';
                
        // Étape 5 : Générer et afficher les onglets
        const tabs = generateTabs(user.role);
        renderTabs(tabs);
                
        // Cacher le chargement
        document.getElementById('loading').style.display = 'none';
                
    } catch (error) {
        console.error('Erreur d\'initialisation:', error);
        showError('❌ Une erreur est survenue. Veuillez réessayer.');
    }
}

// Lancer l'application au chargement de la page
window.addEventListener('DOMContentLoaded', initApp);