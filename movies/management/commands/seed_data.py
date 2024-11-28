import os
from django.core.management.base import BaseCommand
from movies.models import Movie, Genre, Review, MovieImage
from django.core.files import File


class Command(BaseCommand):
    help = 'Seeds the database with example data'

    def handle(self, *args, **kwargs):
        # Очистка базы данных
        self.stdout.write('Deleting old data...')
        Movie.objects.all().delete()
        Genre.objects.all().delete()
        Review.objects.all().delete()

        # Создание жанров
        self.stdout.write('Creating genres...')
        genres = ['Action', 'Comedy', 'Horror', 'Sci-Fi', 'Drama',
                  'Crime', 'Romance', 'Adventure', 'Animation', 'Biography', 'Fantasy', 'Thriller']
        for genre in genres:
            Genre.objects.get_or_create(name=genre)

        # Создание фильмов
        self.stdout.write('Creating movies...')
        movie_data = [
            {
                'title': 'BangGang: The Incredible Adventures of Igor and Alexandra',
                'description': 'In a world where coding is magic and Wi-Fi is the only thing keeping '
                               'society from collapsing, Igor and Alexandra embark on a whirlwind journey to reclaim '
                               'their self-esteem. Along the way, they must face a bunch of '
                               'ridiculous and menacing evil champions,'
                               ' including the Function Overlord, the Debug King, '
                               'and the dreaded SQL Witch, each presenting '
                               'increasingly bizarre challenges that test their wits, '
                               'courage, and capacity for absurdity.',
                'release_date': '2023-12-17',
                'duration': 525600,
                'image': 'movies/sample_images/BangBang.jpg',
                'genres': ['Sci-Fi', 'Action']
            },
            {
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology.',
                'release_date': '2010-07-16',
                'duration': 148,
                'image': 'movies/sample_images/inception.jpg',
                'genres': ['Sci-Fi', 'Action']
            },
            {
                'title': 'The Matrix',
                'description': 'A computer hacker learns about the true nature of reality.',
                'release_date': '1999-03-31',
                'duration': 136,
                'is_highlight': True,
                'image': 'movies/sample_images/matrix.jpg',
                'genres': ['Sci-Fi', 'Action'],
                'extra_images': [
                    'movies/sample_images/extra/matrix_1.jpg',
                ]
            },
            {
                'title': 'The Dark Knight',
                'description': 'Batman faces the Joker, a criminal '
                               'mastermind who wants to create chaos in Gotham City.',
                'release_date': '2008-07-18',
                'duration': 152,
                'image': 'movies/sample_images/dark_knight.jpg',
                'genres': ['Action', 'Drama']
            },
            {
                'title': 'Interstellar',
                'description': 'A group of astronauts travels through a wormhole in search of a new home for humanity.',
                'release_date': '2014-11-07',
                'duration': 169,
                'image': 'movies/sample_images/interstellar.jpg',
                'genres': ['Sci-Fi', 'Drama']
            },
            {
                'title': 'Pulp Fiction',
                'description': 'The lives of two mob hitmen, a boxer, a gangster, '
                               'and his wife intertwine in a series of stories.',
                'release_date': '1994-10-14',
                'duration': 154,
                'image': 'movies/sample_images/pulp_fiction.jpg',
                'genres': ['Drama', 'Crime']
            },
            {
                'title': 'The Shawshank Redemption',
                'description': 'Two imprisoned men bond over a number of years, '
                               'finding solace and eventual redemption.',
                'release_date': '1994-09-22',
                'duration': 142,
                'image': 'movies/sample_images/shawshank.jpg',
                'genres': ['Drama', 'Crime']
            },
            {
                'title': 'Forrest Gump',
                'description': 'The story of a slow-witted but kind-hearted '
                               'man and his extraordinary journey through life.',
                'release_date': '1994-07-06',
                'duration': 142,
                'image': 'movies/sample_images/forrest_gump.jpg',
                'genres': ['Drama', 'Romance']
            },
            {
                'title': 'Gladiator',
                'description': 'A betrayed Roman general fights for his freedom '
                               'and the chance to avenge his family.',
                'release_date': '2000-05-05',
                'duration': 155,
                'is_highlight': True,
                'image': 'movies/sample_images/gladiator.jpg',
                'genres': ['Action', 'Drama'],
                'extra_images': [
                    'movies/sample_images/extra/gladiator_1.jpg',
                ]
            },
            {
                'title': 'Titanic',
                'description': 'A romance blooms aboard the ill-fated R.M.S. Titanic.',
                'release_date': '1997-12-19',
                'duration': 195,
                'image': 'movies/sample_images/titanic.jpg',
                'genres': ['Drama', 'Romance']
            },
            {
                'title': 'Jurassic Park',
                'description': 'During a preview tour, a theme park suffers a major '
                               'power breakdown that unleashes dinosaurs.',
                'release_date': '1993-06-11',
                'duration': 127,
                'image': 'movies/sample_images/jurassic_park.jpg',
                'genres': ['Sci-Fi', 'Adventure']
            },
            {
                'title': 'The Godfather',
                'description': 'The aging patriarch of an organized crime dynasty '
                               'transfers control to his reluctant son.',
                'release_date': '1972-03-24',
                'duration': 175,
                'image': 'movies/sample_images/godfather.jpg',
                'genres': ['Crime', 'Drama']
            },
            {
                'title': 'The Lord of the Rings: The Fellowship of the Ring',
                'description': 'A hobbit and his companions set out to destroy the One Ring and save Middle-earth.',
                'release_date': '2001-12-19',
                'duration': 178,
                'image': 'movies/sample_images/fellowship.jpg',
                'genres': ['Fantasy', 'Adventure']
            },
            {
                'title': 'The Lion King',
                'description': 'A young lion prince flees his kingdom after the '
                               'murder of his father, but learns his destiny.',
                'release_date': '1994-06-24',
                'duration': 88,
                'image': 'movies/sample_images/lion_king.jpg',
                'genres': ['Animation', 'Adventure']
            },
            {
                'title': 'Fight Club',
                'description': 'An insomniac office worker and a soap salesman form an underground fight club.',
                'release_date': '1999-10-15',
                'duration': 139,
                'image': 'movies/sample_images/fight_club.jpg',
                'genres': ['Drama', 'Thriller']
            },
            {
                'title': 'Avatar',
                'description': 'A paraplegic Marine is sent to Pandora on a '
                               'unique mission but becomes torn between two worlds.',
                'release_date': '2009-12-18',
                'duration': 162,
                'image': 'movies/sample_images/avatar.jpg',
                'genres': ['Sci-Fi', 'Adventure']
            },
            {
                'title': 'The Avengers',
                'description': 'Earth’s mightiest heroes must come together to stop Loki from enslaving humanity.',
                'release_date': '2012-05-04',
                'duration': 143,
                'image': 'movies/sample_images/avengers.jpg',
                'genres': ['Action', 'Sci-Fi']
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'description': 'An orphan discovers he is a wizard and attends a magical school.',
                'release_date': '2001-11-16',
                'duration': 152,
                'image': 'movies/sample_images/harry_potter.jpg',
                'genres': ['Fantasy', 'Adventure']
            },
            {
                'title': 'The Wolf of Wall Street',
                'description': 'The true story of Jordan Belfort and his rise and fall as a wealthy stockbroker.',
                'release_date': '2013-12-25',
                'duration': 180,
                'image': 'movies/sample_images/wolf_wall_street.jpg',
                'genres': ['Biography', 'Comedy']
            },
            {
                'title': 'Dune',
                'description': 'Paul Atreides leads nomadic tribes in a battle to control the desert planet Arrakis.',
                'release_date': '2021-10-22',
                'duration': 155,
                'is_highlight': True,
                'image': 'movies/sample_images/dune.jpg',
                'genres': ['Sci-Fi', 'Adventure'],
                'extra_images': [
                    'movies/sample_images/extra/dune_1.jpg',
                ]
            },
        ]

        for movie in movie_data:
            m = Movie(
                title=movie['title'],
                description=movie['description'],
                release_date=movie['release_date'],
                duration=movie['duration'],
                is_highlight=movie.get('is_highlight', False)
            )
            # Загружаем изображение
            image_path = movie['image']
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    m.image.save(os.path.basename(image_path), File(img_file), save=False)
            m.save()

            # Привязка жанров
            for genre_name in movie['genres']:
                genre = Genre.objects.get(name=genre_name)
                m.genres.add(genre)

            # Загрузка дополнительных изображений
            for extra_image_path in movie.get('extra_images', []):
                if os.path.exists(extra_image_path):
                    with open(extra_image_path, 'rb') as img_file:
                        extra_image = MovieImage(
                            movie=m,
                        )
                        extra_image.image.save(os.path.basename(extra_image_path), File(img_file), save=True)

        # # Создание пользователя и отзывов
        # self.stdout.write('Creating user and reviews...')
        # user = User.objects.create_user(username='admin', password='admin')
        # for movie in Movie.objects.all():
        #     Review.objects.create(
        #         user=user,
        #         movie=movie,
        #         text='This is an example review for ' + movie.title,
        #     )

        self.stdout.write('Seeding complete!')
