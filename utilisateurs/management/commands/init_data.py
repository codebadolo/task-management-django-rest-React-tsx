# utilisateurs/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from utilisateurs.models import Department, Section, Poste, Competence
from taches.models import Project, Task, TaskComment, Notification
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données de test avec des noms burkinabè'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Début de la génération des données...'))
        
        # 1. Créer les postes
        self.creer_postes()
        
        # 2. Créer le directeur général
        self.creer_directeur()
        
        # 3. Créer le coordinateur général
        self.creer_coordinateur()
        
        # 4. Créer les départements avec leurs chefs
        self.creer_departements()
        
        # 5. Créer l'admin système
        self.creer_admin()
        
        # 6. Créer des projets et tâches
        self.creer_projets_et_taches()
        
        self.stdout.write(self.style.SUCCESS('✓ Génération terminée avec succès!'))

    def creer_postes(self):
        """Créer les postes nécessaires"""
        postes_data = [
            # Postes de direction
            {'titre': 'Directeur Général', 'code': 'DG', 'categorie': 'direction', 
             'niveau_hierarchique': 10, 'peut_gerer_equipe': True, 'peut_creer_projets': True,
             'peut_valider_taches': True, 'color': '#9b2c2c', 'icon': 'fa-solid fa-crown'},
            
            # Coordinateur général
            {'titre': 'Coordinateur Général', 'code': 'CG', 'categorie': 'direction',
             'niveau_hierarchique': 9, 'peut_gerer_equipe': True, 'peut_creer_projets': True,
             'peut_valider_taches': True, 'color': '#8e44ad', 'icon': 'fa-solid fa-chart-line'},
            
            # Chefs de département
            {'titre': 'Chef de Département Production', 'code': 'CDP', 'categorie': 'direction',
             'niveau_hierarchique': 8, 'peut_gerer_equipe': True, 'peut_creer_projets': True,
             'peut_valider_taches': True, 'color': '#e67e22', 'icon': 'fa-solid fa-industry'},
            {'titre': 'Chef de Département IT', 'code': 'CDI', 'categorie': 'direction',
             'niveau_hierarchique': 8, 'peut_gerer_equipe': True, 'peut_creer_projets': True,
             'peut_valider_taches': True, 'color': '#2980b9', 'icon': 'fa-solid fa-laptop'},
            {'titre': 'Chef de Département RH', 'code': 'CDR', 'categorie': 'direction',
             'niveau_hierarchique': 8, 'peut_gerer_equipe': True, 'peut_creer_projets': True,
             'peut_valider_taches': True, 'color': '#27ae60', 'icon': 'fa-solid fa-users'},
            
            # Responsables de section
            {'titre': 'Responsable CM', 'code': 'RCM', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#f39c12', 'icon': 'fa-solid fa-bullhorn'},
            {'titre': 'Responsable Graphisme', 'code': 'RGR', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#8e44ad', 'icon': 'fa-solid fa-paint-brush'},
            {'titre': 'Responsable Photographie', 'code': 'RPH', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#16a085', 'icon': 'fa-solid fa-camera'},
            {'titre': 'Responsable Vidéo', 'code': 'RVD', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#c0392b', 'icon': 'fa-solid fa-video'},
            {'titre': 'Responsable Développement', 'code': 'RDEV', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#3498db', 'icon': 'fa-solid fa-code'},
            {'titre': 'Responsable Infrastructure', 'code': 'RINF', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#34495e', 'icon': 'fa-solid fa-server'},
            {'titre': 'Responsable Administration RH', 'code': 'RADM', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#2ecc71', 'icon': 'fa-solid fa-user-tie'},
            {'titre': 'Responsable Paie', 'code': 'RPAIE', 'categorie': 'management',
             'niveau_hierarchique': 6, 'peut_gerer_equipe': True, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#27ae60', 'icon': 'fa-solid fa-calculator'},
            
            # Postes techniques
            {'titre': 'Community Manager', 'code': 'CM', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#f39c12', 'icon': 'fa-solid fa-hashtag'},
            {'titre': 'Graphiste Senior', 'code': 'GRS', 'categorie': 'technique',
             'niveau_hierarchique': 5, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#9b59b6', 'icon': 'fa-solid fa-pen-fancy'},
            {'titre': 'Graphiste Junior', 'code': 'GRJ', 'categorie': 'technique',
             'niveau_hierarchique': 3, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#8e44ad', 'icon': 'fa-solid fa-pen'},
            {'titre': 'Photographe', 'code': 'PHO', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#1abc9c', 'icon': 'fa-solid fa-camera-retro'},
            {'titre': 'Vidéaste', 'code': 'VID', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#e74c3c', 'icon': 'fa-solid fa-film'},
            {'titre': 'Monteur Vidéo', 'code': 'MON', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#c0392b', 'icon': 'fa-solid fa-cut'},
            {'titre': 'Développeur Full Stack', 'code': 'DFS', 'categorie': 'technique',
             'niveau_hierarchique': 5, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#2980b9', 'icon': 'fa-solid fa-laptop-code'},
            {'titre': 'Développeur Frontend', 'code': 'DFE', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#3498db', 'icon': 'fa-solid fa-code'},
            {'titre': 'Développeur Backend', 'code': 'DBE', 'categorie': 'technique',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#2c3e50', 'icon': 'fa-solid fa-database'},
            {'titre': 'Administrateur Système', 'code': 'SYS', 'categorie': 'technique',
             'niveau_hierarchique': 5, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': True, 'color': '#34495e', 'icon': 'fa-solid fa-server'},
            {'titre': 'Chargé RH', 'code': 'CRH', 'categorie': 'administratif',
             'niveau_hierarchique': 4, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#27ae60', 'icon': 'fa-solid fa-user-tie'},
            {'titre': 'Assistant RH', 'code': 'ARH', 'categorie': 'administratif',
             'niveau_hierarchique': 3, 'peut_gerer_equipe': False, 'peut_creer_projets': False,
             'peut_valider_taches': False, 'color': '#2ecc71', 'icon': 'fa-solid fa-user-clock'},
        ]
        
        for poste_data in postes_data:
            poste, created = Poste.objects.get_or_create(
                code=poste_data['code'],
                defaults=poste_data
            )
            if created:
                self.stdout.write(f"  ✓ Poste créé: {poste.titre}")
            else:
                self.stdout.write(f"  • Poste existant: {poste.titre}")

    def creer_directeur(self):
        """Créer le directeur général"""
        directeur_data = {
            'email': 'directeur@company.bf',
            'first_name': 'Abdoulaye',
            'last_name': 'COMPAORÉ',
            'role': 'directeur',
            'poste': Poste.objects.get(code='DG'),
            'phone': '70 12 34 56',
            'ville': 'Ouagadougou',
            'date_naissance': '1975-05-15',
            'date_embauche': '2010-01-10',
            'is_staff': True,
            'is_superuser': True,
        }
        
        directeur, created = User.objects.get_or_create(
            email=directeur_data['email'],
            defaults=directeur_data
        )
        if created:
            directeur.set_password('directeur123')
            directeur.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Directeur créé: {directeur.get_full_name()}"))
        else:
            self.stdout.write(f"  • Directeur existant: {directeur.get_full_name()}")

    def creer_coordinateur(self):
        """Créer le coordinateur général"""
        coord_data = {
            'email': 'coordinateur@company.bf',
            'first_name': 'Mamadou',
            'last_name': 'OUÉDRAOGO',
            'role': 'coordinateur',
            'poste': Poste.objects.get(code='CG'),
            'phone': '71 23 45 67',
            'ville': 'Ouagadougou',
            'date_naissance': '1980-08-20',
            'date_embauche': '2015-03-15',
            'is_staff': True,
        }
        
        coord, created = User.objects.get_or_create(
            email=coord_data['email'],
            defaults=coord_data
        )
        if created:
            coord.set_password('coord123')
            coord.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Coordinateur créé: {coord.get_full_name()}"))
        else:
            self.stdout.write(f"  • Coordinateur existant: {coord.get_full_name()}")

    def creer_departements(self):
        """Créer les départements avec leurs chefs et sections"""
        
        # Données des départements
        deps_data = [
            {
                'name': 'Production',
                'code': 'PROD',
                'color': '#e67e22',
                'icon': 'fa-solid fa-industry',
                'chef': {
                    'email': 'chef.production@company.bf',
                    'first_name': 'Moussa',
                    'last_name': 'OUÉDRAOGO',
                    'phone': '71 23 45 67',
                },
                'sections': [
                    {
                        'name': 'CM',
                        'code': 'CM',
                        'color': '#f39c12',
                        'responsable': {
                            'email': 'responsable.cm@company.bf',
                            'first_name': 'Aïssata',
                            'last_name': 'KABORÉ',
                        },
                        'poste_resp': 'RCM',
                        'poste_membre': 'CM',
                        'membres': [
                            ('Aminata', 'SANA', '70 98 76 54'),
                            ('Boukary', 'ZONGO', '71 87 65 43'),
                            ('Fatimata', 'TRAORÉ', '72 76 54 32'),
                            ('Issouf', 'SAWADOGO', '73 65 43 21'),
                        ]
                    },
                    {
                        'name': 'Graphisme',
                        'code': 'GRAPH',
                        'color': '#8e44ad',
                        'responsable': {
                            'email': 'responsable.graphisme@company.bf',
                            'first_name': 'Salif',
                            'last_name': 'DIALLO',
                        },
                        'poste_resp': 'RGR',
                        'poste_membre': 'GRS',
                        'membres': [
                            ('Mariam', 'BARRY', '70 12 34 56', 'GRS'),
                            ('Adama', 'COMPAORÉ', '71 23 45 67', 'GRS'),
                            ('Rokia', 'OUATTARA', '72 34 56 78', 'GRJ'),
                            ('Ibrahim', 'SANOGO', '73 45 67 89', 'GRJ'),
                        ]
                    },
                    {
                        'name': 'Photographie',
                        'code': 'PHOTO',
                        'color': '#16a085',
                        'responsable': {
                            'email': 'responsable.photo@company.bf',
                            'first_name': 'Kadiatou',
                            'last_name': 'CISSÉ',
                        },
                        'poste_resp': 'RPH',
                        'poste_membre': 'PHO',
                        'membres': [
                            ('Mamadou', 'KONATÉ', '74 56 78 90'),
                            ('Bintou', 'DICKO', '75 67 89 01'),
                            ('Ousmane', 'TRAORÉ', '76 78 90 12'),
                            ('Ramatou', 'SOULAMA', '77 89 01 23'),
                        ]
                    },
                    {
                        'name': 'Vidéaste',
                        'code': 'VIDEO',
                        'color': '#c0392b',
                        'responsable': {
                            'email': 'responsable.video@company.bf',
                            'first_name': 'Souleymane',
                            'last_name': 'ZONGO',
                        },
                        'poste_resp': 'RVD',
                        'poste_membre': 'VID',
                        'membres': [
                            ('Rasmané', 'OUÉDRAOGO', '78 90 12 34'),
                            ('Alizèta', 'KABORÉ', '79 01 23 45'),
                            ('Bakary', 'SANOU', '70 11 22 33'),
                            ('Dramane', 'KONÉ', '71 22 33 44', 'MON'),
                        ]
                    },
                ]
            },
            {
                'name': 'IT',
                'code': 'IT',
                'color': '#2980b9',
                'icon': 'fa-solid fa-laptop',
                'chef': {
                    'email': 'chef.it@company.bf',
                    'first_name': 'Drissa',
                    'last_name': 'TRAORÉ',
                    'phone': '72 34 56 78',
                },
                'sections': [
                    {
                        'name': 'Développement',
                        'code': 'DEV',
                        'color': '#3498db',
                        'responsable': {
                            'email': 'responsable.dev@company.bf',
                            'first_name': 'Alassane',
                            'last_name': 'DRABO',
                        },
                        'poste_resp': 'RDEV',
                        'poste_membre': 'DFS',
                        'membres': [
                            ('Tégawindé', 'YAMÉOGO', '70 44 55 66', 'DFS'),
                            ('Maimouna', 'TIENDREBÉOGO', '71 55 66 77', 'DFE'),
                            ('Wendlasida', 'OUÉDRAOGO', '72 66 77 88', 'DBE'),
                            ('Palgwendé', 'COMPAORÉ', '73 77 88 99', 'DFE'),
                            ('Arouna', 'TRAORÉ', '74 88 99 00', 'DBE'),
                        ]
                    },
                    {
                        'name': 'Infrastructure',
                        'code': 'INFRA',
                        'color': '#34495e',
                        'responsable': {
                            'email': 'responsable.infra@company.bf',
                            'first_name': 'Hamidou',
                            'last_name': 'BARRY',
                        },
                        'poste_resp': 'RINF',
                        'poste_membre': 'SYS',
                        'membres': [
                            ('Daouda', 'OUÉDRAOGO', '74 88 99 00'),
                            ('Barkissa', 'SORÉ', '75 99 00 11'),
                            ('Yacouba', 'SAWADOGO', '76 00 11 22'),
                            ('Salimata', 'BONKIAN', '77 11 22 33'),
                        ]
                    },
                ]
            },
            {
                'name': 'Ressources Humaines',
                'code': 'RH',
                'color': '#27ae60',
                'icon': 'fa-solid fa-users',
                'chef': {
                    'email': 'chef.rh@company.bf',
                    'first_name': 'Awa',
                    'last_name': 'BARRY',
                    'phone': '73 45 67 89',
                },
                'sections': [
                    {
                        'name': 'Administration',
                        'code': 'ADMIN',
                        'color': '#2ecc71',
                        'responsable': {
                            'email': 'responsable.admin@company.bf',
                            'first_name': 'Mariama',
                            'last_name': 'COMPAORÉ',
                        },
                        'poste_resp': 'RADM',
                        'poste_membre': 'CRH',
                        'membres': [
                            ('Madi', 'PALENFO', '78 22 33 44'),
                            ('Asséta', 'KABORÉ', '79 33 44 55'),
                            ('Mamadou', 'SANA', '70 44 55 66'),
                            ('Halimatou', 'ZONGO', '71 55 66 77'),
                        ]
                    },
                    {
                        'name': 'Paie',
                        'code': 'PAIE',
                        'color': '#27ae60',
                        'responsable': {
                            'email': 'responsable.paie@company.bf',
                            'first_name': 'Boureima',
                            'last_name': 'OUÉDRAOGO',
                        },
                        'poste_resp': 'RPAIE',
                        'poste_membre': 'ARH',
                        'membres': [
                            ('Kadidia', 'SANOU', '72 66 77 88'),
                            ('Seydou', 'TRAORÉ', '73 77 88 99'),
                            ('Aminata', 'BARRO', '74 88 99 00'),
                            ('Oumar', 'DIALLO', '75 99 00 11'),
                        ]
                    },
                ]
            },
        ]
        
        # Création des départements
        for dep_data in deps_data:
            # Créer le département
            department, created = Department.objects.get_or_create(
                code=dep_data['code'],
                defaults={
                    'name': dep_data['name'],
                    'color': dep_data['color'],
                    'icon': dep_data['icon'],
                }
            )
            if created:
                self.stdout.write(f"  ✓ Département créé: {department.name}")
            
            # Créer le chef de département
            chef_data = dep_data['chef']
            chef, created = User.objects.get_or_create(
                email=chef_data['email'],
                defaults={
                    'first_name': chef_data['first_name'],
                    'last_name': chef_data['last_name'],
                    'role': 'coordinateur',
                    'poste': Poste.objects.get(code=f'CD{dep_data["code"][0]}'),
                    'department': department,
                    'phone': chef_data['phone'],
                    'ville': 'Ouagadougou',
                    'is_staff': True,
                }
            )
            if created:
                chef.set_password('chef123')
                chef.save()
                self.stdout.write(f"    ✓ Chef créé: {chef.get_full_name()}")
            
            # Créer les sections
            for section_data in dep_data['sections']:
                # Créer la section
                section, created = Section.objects.get_or_create(
                    code=section_data['code'],
                    department=department,
                    defaults={
                        'name': section_data['name'],
                        'color': section_data['color'],
                    }
                )
                if created:
                    self.stdout.write(f"      ✓ Section créée: {section.name}")
                
                # Créer le responsable de section
                resp_data = section_data['responsable']
                responsable, created = User.objects.get_or_create(
                    email=resp_data['email'],
                    defaults={
                        'first_name': resp_data['first_name'],
                        'last_name': resp_data['last_name'],
                        'role': 'responsable_section',
                        'poste': Poste.objects.get(code=section_data['poste_resp']),
                        'department': department,
                        'section': section,
                        'phone': f'70 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}',
                        'ville': 'Ouagadougou',
                        'is_staff': True,
                    }
                )
                if created:
                    responsable.set_password('responsable123')
                    responsable.save()
                    self.stdout.write(f"        ✓ Responsable créé: {responsable.get_full_name()}")
                
                # Mettre à jour la section avec le responsable
                section.responsable = responsable
                section.save()
                
                # Créer les membres de la section
                for membre_data in section_data['membres']:
                    if len(membre_data) == 4:
                        prenom, nom, phone, poste_code = membre_data
                    else:
                        prenom, nom, phone = membre_data
                        poste_code = section_data['poste_membre']
                    
                    poste = Poste.objects.get(code=poste_code)
                    membre_email = f"{prenom.lower()}.{nom.lower()}@company.bf".replace('é', 'e').replace('è', 'e').replace('ô', 'o')
                    
                    membre, created = User.objects.get_or_create(
                        email=membre_email,
                        defaults={
                            'first_name': prenom,
                            'last_name': nom,
                            'role': 'membre',
                            'poste': poste,
                            'department': department,
                            'section': section,
                            'phone': phone,
                            'ville': 'Ouagadougou',
                        }
                    )
                    if created:
                        membre.set_password('membre123')
                        membre.save()

    def creer_admin(self):
        """Créer l'administrateur système"""
        admin, created = User.objects.get_or_create(
            email='admin@company.bf',
            defaults={
                'first_name': 'Admin',
                'last_name': 'SYSTEME',
                'role': 'directeur',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Admin créé: {admin.email}"))
        else:
            self.stdout.write(f"  • Admin existant: {admin.email}")

    def creer_projets_et_taches(self):
        """Créer des projets et des tâches"""
        today = timezone.now().date()
        
        # Récupérer les départements
        prod_dept = Department.objects.get(code='PROD')
        it_dept = Department.objects.get(code='IT')
        rh_dept = Department.objects.get(code='RH')
        
        # Récupérer les coordinateurs
        coord_general = User.objects.get(email='coordinateur@company.bf')
        
        # Projets Production
        projets_data = [
            {
                'name': 'Campagne Publicitaire Télévision BF1',
                'code': 'CAMP-TV-2026',
                'description': '''Création d'une campagne publicitaire complète pour la télévision nationale BF1.
                Objectifs :
                - Créer 3 spots TV de 30 secondes
                - Réaliser des photos pour les supports print
                - Développer une stratégie de communication sur les réseaux sociaux
                - Former les équipes à la gestion des réseaux sociaux''',
                'department': prod_dept,
                'priority': 5,
                'start_date': today,
                'end_date': today + timedelta(days=90),
                'coordinators': [coord_general],
                'sections': ['CM', 'GRAPH', 'PHOTO', 'VIDEO'],
                'tasks': [
                    {
                        'title': 'Brief créatif avec le client',
                        'description': '''Organiser une réunion de briefing avec les équipes de BF1 pour comprendre :
                        - Leurs attentes
                        - Leur image de marque
                        - Leurs cibles
                        - Leurs contraintes techniques''',
                        'assigned_section': 'CM',
                        'priority': 5,
                        'complexity': 3,
                        'due_days': 3,
                    },
                    {
                        'title': 'Création du concept créatif',
                        'description': '''Développer 3 concepts créatifs différents :
                        - Concept humoristique
                        - Concept émotionnel
                        - Concept informatif
                        Présenter les storyboards et moodboards''',
                        'assigned_section': 'GRAPH',
                        'priority': 5,
                        'complexity': 4,
                        'due_days': 10,
                    },
                    {
                        'title': 'Tournage des spots TV',
                        'description': '''Organiser et réaliser le tournage des 3 spots TV :
                        - Location de matériel
                        - Casting des acteurs
                        - Tournage en extérieur et en studio
                        - Prises de vue supplémentaires pour les photos''',
                        'assigned_section': 'VIDEO',
                        'priority': 5,
                        'complexity': 5,
                        'due_days': 25,
                    },
                    {
                        'title': 'Séance photo produit',
                        'description': '''Réaliser une séance photo professionnelle :
                        - Photos des produits
                        - Photos d'ambiance
                        - Portraits des équipes
                        - Retouches photo''',
                        'assigned_section': 'PHOTO',
                        'priority': 4,
                        'complexity': 3,
                        'due_days': 20,
                    },
                    {
                        'title': 'Montage et post-production',
                        'description': '''Assurer le montage des spots :
                        - Montage vidéo
                        - Étalonnage
                        - Mixage audio
                        - Ajout d'effets spéciaux
                        - Sous-titrage''',
                        'assigned_section': 'VIDEO',
                        'priority': 5,
                        'complexity': 4,
                        'due_days': 40,
                    },
                    {
                        'title': 'Création des visuels print',
                        'description': '''Concevoir les supports print :
                        - Affiches grand format
                        - Flyers
                        - Bannières pour sites web
                        - Habillage des véhicules''',
                        'assigned_section': 'GRAPH',
                        'priority': 4,
                        'complexity': 3,
                        'due_days': 35,
                    },
                    {
                        'title': 'Stratégie réseaux sociaux',
                        'description': '''Élaborer une stratégie complète :
                        - Calendrier éditorial
                        - Création de contenu
                        - Planning des publications
                        - Gestion des communautés
                        - Analyse des performances''',
                        'assigned_section': 'CM',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 15,
                    },
                    {
                        'title': 'Formation des équipes',
                        'description': '''Former les équipes de BF1 :
                        - Utilisation des réseaux sociaux
                        - Gestion de communauté
                        - Création de contenu basique
                        - Analyse des statistiques''',
                        'assigned_section': 'CM',
                        'priority': 3,
                        'complexity': 3,
                        'due_days': 70,
                    },
                ]
            },
            {
                'name': 'Refonte Identité Visuelle Groupe Wendkuni',
                'code': 'IDV-WEND-2026',
                'description': '''Refonte complète de l'identité visuelle du Groupe Wendkuni (hôtels, restaurants, agences de voyage).
                Objectifs :
                - Nouveau logo
                - Charte graphique complète
                - Supports de communication
                - Signalétique hôtelière
                - Formation des équipes''',
                'department': prod_dept,
                'priority': 4,
                'start_date': today + timedelta(days=15),
                'end_date': today + timedelta(days=120),
                'coordinators': [coord_general],
                'sections': ['GRAPH', 'PHOTO'],
                'tasks': [
                    {
                        'title': 'Audit de l\'existant',
                        'description': '''Analyser l'identité visuelle actuelle :
                        - Points forts et faibles
                        - Cohérence entre les entités
                        - Perception client
                        - Recommandations''',
                        'assigned_section': 'GRAPH',
                        'priority': 4,
                        'complexity': 3,
                        'due_days': 7,
                    },
                    {
                        'title': 'Création du nouveau logo',
                        'description': '''Proposer 5 concepts de logo :
                        - Version principale
                        - Variantes monochromes
                        - Adaptations pour fonds colorés
                        - Déclinaisons pour sous-marques''',
                        'assigned_section': 'GRAPH',
                        'priority': 5,
                        'complexity': 5,
                        'due_days': 20,
                    },
                    {
                        'title': 'Charte graphique complète',
                        'description': '''Rédiger la charte graphique détaillée :
                        - Palette de couleurs
                        - Typographies
                        - Règles d'utilisation du logo
                        - Papeterie (cartes de visite, en-têtes)
                        - Templates documents''',
                        'assigned_section': 'GRAPH',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 40,
                    },
                    {
                        'title': 'Shooting photo établissements',
                        'description': '''Réaliser des photos professionnelles :
                        - Hôtels (chambres, halls, piscines)
                        - Restaurants (plats, ambiance)
                        - Équipes en action
                        - Photos aériennes par drone''',
                        'assigned_section': 'PHOTO',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 30,
                    },
                ]
            },
            {
                'name': 'Développement Application Mobile Yamba',
                'code': 'APP-YAMBA-2026',
                'description': '''Développement d'une application mobile de e-commerce pour la marque Yamba (artisanat burkinabè).
                Objectifs :
                - Application Android et iOS
                - Catalogue produits
                - Paiement mobile (Orange Money, Moov Money)
                - Gestion des commandes
                - Interface administrateur''',
                'department': it_dept,
                'priority': 5,
                'start_date': today,
                'end_date': today + timedelta(days=180),
                'coordinators': [coord_general],
                'sections': ['DEV', 'GRAPH'],
                'tasks': [
                    {
                        'title': 'Spécifications fonctionnelles',
                        'description': '''Rédiger le cahier des charges :
                        - Fonctionnalités principales
                        - Parcours utilisateur
                        - Contraintes techniques
                        - Budget et délais''',
                        'assigned_section': 'DEV',
                        'priority': 5,
                        'complexity': 3,
                        'due_days': 10,
                    },
                    {
                        'title': 'Maquettage UI/UX',
                        'description': '''Créer les maquettes de l'application :
                        - Wireframes
                        - Design system
                        - Prototype interactif
                        - Tests utilisateurs''',
                        'assigned_section': 'GRAPH',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 20,
                    },
                    {
                        'title': 'Développement Backend API',
                        'description': '''Développer l'API RESTful :
                        - Base de données
                        - Authentification JWT
                        - Gestion des produits
                        - Gestion des commandes
                        - Intégration paiements''',
                        'assigned_section': 'DEV',
                        'priority': 5,
                        'complexity': 5,
                        'due_days': 60,
                    },
                    {
                        'title': 'Développement Application Android',
                        'description': '''Développer l'application Android :
                        - Interface utilisateur
                        - Appels API
                        - Gestion hors-ligne
                        - Notifications push''',
                        'assigned_section': 'DEV',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 90,
                    },
                    {
                        'title': 'Développement Application iOS',
                        'description': '''Développer l'application iOS :
                        - Interface utilisateur
                        - Appels API
                        - Gestion hors-ligne
                        - Notifications push''',
                        'assigned_section': 'DEV',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 120,
                    },
                    {
                        'title': 'Tests et recette',
                        'description': '''Effectuer les tests complets :
                        - Tests fonctionnels
                        - Tests de charge
                        - Tests de sécurité
                        - Correction des bugs''',
                        'assigned_section': 'DEV',
                        'priority': 5,
                        'complexity': 3,
                        'due_days': 150,
                    },
                ]
            },
            {
                'name': 'Campagne de Recrutement 2026',
                'code': 'RECRUT-2026',
                'description': '''Campagne de recrutement pour 50 nouveaux talents.
                Objectifs :
                - Publication des offres
                - Présélection des candidats
                - Organisation des entretiens
                - Intégration des nouveaux employés''',
                'department': rh_dept,
                'priority': 4,
                'start_date': today + timedelta(days=5),
                'end_date': today + timedelta(days=60),
                'coordinators': [coord_general],
                'sections': ['ADMIN', 'PAIE'],
                'tasks': [
                    {
                        'title': 'Rédaction des offres',
                        'description': '''Rédiger 15 offres d'emploi :
                        - Profils techniques (IT)
                        - Profils créatifs (Production)
                        - Profils administratifs (RH)
                        - Diffusion sur les plateformes''',
                        'assigned_section': 'ADMIN',
                        'priority': 5,
                        'complexity': 3,
                        'due_days': 5,
                    },
                    {
                        'title': 'Présélection CV',
                        'description': '''Analyser les candidatures :
                        - Tri des CV
                        - Tests techniques
                        - Présélection pour entretiens''',
                        'assigned_section': 'ADMIN',
                        'priority': 4,
                        'complexity': 4,
                        'due_days': 20,
                    },
                    {
                        'title': 'Organisation entretiens',
                        'description': '''Planifier et organiser les entretiens :
                        - Coordination avec les managers
                        - Planning des entretiens
                        - Préparation des grilles d'évaluation''',
                        'assigned_section': 'ADMIN',
                        'priority': 4,
                        'complexity': 3,
                        'due_days': 25,
                    },
                    {
                        'title': 'Préparation contrats',
                        'description': '''Préparer les dossiers administratifs :
                        - Contrats de travail
                        - Déclarations CNSS
                        - Mutuelle santé
                        - Dossiers d'intégration''',
                        'assigned_section': 'PAIE',
                        'priority': 4,
                        'complexity': 3,
                        'due_days': 45,
                    },
                ]
            },
        ]
        
        # Création des projets et tâches
        for proj_data in projets_data:
            # Créer le projet
            project, created = Project.objects.get_or_create(
                code=proj_data['code'],
                defaults={
                    'name': proj_data['name'],
                    'description': proj_data['description'],
                    'department': proj_data['department'],
                    'priority': proj_data['priority'],
                    'start_date': proj_data['start_date'],
                    'end_date': proj_data['end_date'],
                    'created_by': coord_general,
                    'status': random.choice(['planning', 'active']),
                }
            )
            
            if created:
                # Ajouter les coordinateurs
                for coord in proj_data['coordinators']:
                    project.coordinators.add(coord)
                
                self.stdout.write(f"  ✓ Projet créé: {project.name}")
                
                # Créer les tâches
                for task_data in proj_data['tasks']:
                    # Trouver la section assignée
                    section = Section.objects.get(
                        code=task_data['assigned_section'],
                        department=proj_data['department']
                    )
                    
                    # Trouver des utilisateurs de cette section
                    users = User.objects.filter(section=section)[:3]
                    
                    due_date = timezone.now() + timedelta(days=task_data['due_days'])
                    
                    task = Task.objects.create(
                        title=task_data['title'],
                        description=task_data['description'],
                        project=project,
                        created_by=coord_general,
                        priority=task_data['priority'],
                        complexity=task_data['complexity'],
                        due_date=due_date,
                        status=random.choice(['todo', 'in_progress']),
                    )
                    
                    # Assigner les utilisateurs
                    for user in users:
                        task.assigned_to.add(user)
                    
                    # Ajouter des commentaires
                    for i in range(random.randint(1, 3)):
                        comment_user = random.choice(list(users) + [coord_general])
                        TaskComment.objects.create(
                            task=task,
                            user=comment_user,
                            comment=random.choice([
                                "J'ai commencé à travailler sur cette tâche.",
                                "Besoin d'éclaircissements sur certains points.",
                                "J'avance bien, devrait être terminé dans les temps.",
                                "J'attends les retours du client.",
                                "Première version prête pour validation.",
                            ])
                        )
                    
                    # Créer des notifications
                    for user in users:
                        Notification.objects.create(
                            user=user,
                            notification_type='task_assigned',
                            title=f'Nouvelle tâche: {task.title}',
                            message=f'Vous avez été assigné à la tâche "{task.title}" dans le projet {project.name}',
                            task=task,
                            project=project,
                        )
                
                self.stdout.write(f"    ✓ {len(proj_data['tasks'])} tâches créées")
        
        # Statistiques finales
        self.stdout.write(self.style.SUCCESS(f"\n✓ Total projets: {Project.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Total tâches: {Task.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Total commentaires: {TaskComment.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Total notifications: {Notification.objects.count()}"))