// /mariage/app.js

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
        },
        {
            id: 'commentaire',
            title: 'Commentaires',
            icon: '💬',
            description: 'Livre d\'or et messages',
            page: 'commentaire.html'
        }
    ],
    // Onglets SUPPLÉMENTAIRES pour les administrateurs
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
        },
        {
            id: 'commentaire',
            title: 'Commentaires',
            icon: '💬',
            description: 'Livre d\'or et messages',
            page: 'commentaire.html'
        }
    ]
};

// Variable globale pour stocker les utilisateurs
let USERS_DB = null;

// Fonction pour charger les utilisateurs
async function loadUsers() {
    try {
        console.log('🔄 Chargement des utilisateurs...');
        const response = await fetch('utilisateur.json', {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Utilisateurs chargés:', data);
        return data;
    } catch (error) {
        console.error('❌ Erreur de chargement:', error);
        
        // Fallback : base de données de test intégrée
        console.warn('⚠️ Utilisation de la base de données de test');
        return {
            'ADMIN001': {
                name: 'Administrateur Principal',
                role: 'admin',
                table: 1
            },
            'GUEST001': {
                name: 'Jean Dupont',
                role: 'guest',
                table: 5
            },
            'GUEST002': {
                name: 'Marie Martin',
                role: 'guest',
                table: 3
            }
        };
    }
}

// Fonction pour extraire le token depuis l'URL
function getTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    console.log('🔑 Token détecté:', token);
    return token;
}

// Fonction pour valider et récupérer le profil utilisateur
function authenticateUser(token) {
    console.log('🔐 Authentification pour:', token);
    console.log('📊 Base de données:', USERS_DB);
    
    if (USERS_DB && USERS_DB[token]) {
        console.log('✅ Utilisateur trouvé:', USERS_DB[token]);
        return {
            success: true,
            user: USERS_DB[token]
        };
    }
    
    console.log('❌ Utilisateur non trouvé');
    return {
        success: false,
        error: 'QR Code invalide ou expiré'
    };
}

// Fonction pour générer les onglets selon le profil
function generateTabs(userRole) {
    console.log('🎨 Génération des onglets pour le rôle:', userRole);
    
    // Tous les utilisateurs ont les onglets communs
    let tabs;
    
   if (userRole === 'admin') {
        // Remplacement TOTAL par les onglets admin
        tabs = [...TABS_CONFIG.admin];
        console.log('👑 Onglets admin UNIQUEMENT');
    } else {
        // Utilisateurs normaux → onglets communs
        tabs = [...TABS_CONFIG.common];
    }
    
    console.log('📋 Total onglets:', tabs.length);
    return tabs;
}

// Fonction pour afficher les onglets
function renderTabs(tabs) {
    console.log('🎭 Affichage de', tabs.length, 'onglets');
    
    const navContainer = document.getElementById('navigation');
    
    if (!navContainer) {
        console.error('❌ Container navigation non trouvé!');
        return;
    }
    
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
    console.log('✅ Onglets affichés');
}

// Fonction pour afficher une erreur
function showError(message) {
    console.error('💥', message);
    const errorDiv = document.getElementById('error');
    const loadingDiv = document.getElementById('loading');
    
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

// Initialisation de l'application
async function initApp() {
    console.log('🚀 Initialisation de l\'application...');
    
    try {
        // Étape 0 : Charger les utilisateurs
        USERS_DB = await loadUsers();
        
        if (!USERS_DB) {
            showError('❌ Impossible de charger la base de données des utilisateurs');
            return;
        }
        
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
        console.log('👤 Utilisateur authentifié:', user);
        
        // Étape 3 : Sauvegarder la session
        sessionStorage.setItem('currentUser', JSON.stringify(user));
        sessionStorage.setItem('authToken', token);
        console.log('💾 Session sauvegardée');
        
        // Étape 4 : Afficher le message de bienvenue
        const userNameElement = document.getElementById('userName');
        const welcomeElement = document.getElementById('welcome');
        
        if (userNameElement) {
            userNameElement.textContent = user.name;
        }
        
        if (welcomeElement) {
            welcomeElement.style.display = 'block';
        }
        
        // Étape 5 : Générer et afficher les onglets
        const tabs = generateTabs(user.role);
        renderTabs(tabs);
        
        // Cacher le chargement
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
        
        console.log('🎉 Application initialisée avec succès!');
        
    } catch (error) {
        console.error('💥 Erreur d\'initialisation:', error);
        showError('❌ Une erreur est survenue. Veuillez réessayer.');
    }
}

// Lancer l'application au chargement de la page
window.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM chargé, lancement de l\'app...');
    initApp();
});