import os
import tempfile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Ingredient, Tag
from recipes.serializers import RecipeSerializer, RecipeDetailSerializer
from PIL import Image


RECIPES_URL = reverse('recipes:recipe-list')


def image_upload_url(recipe_id):
    """Return upload URL"""
    return reverse('recipes:recipe-upload-image', args=(recipe_id,))


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipes:recipe-detail', args=(recipe_id,))


def sample_tag(user, name='Sample Tag'):
    """Create sample Tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Sample Ingredient'):
    """Create sample Ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """Create and return a sample Recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.0
    }
    defaults.update(kwargs)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test public recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test private recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@test.com',
            password='user12345678'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes"""
        sample_recipe(user=self.user, title='Bife con puré')
        sample_recipe(user=self.user, title='Pan de carne')
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes are available only for their authors"""
        user2 = get_user_model().objects.create_user(
            email='other@test.com',
            password='other12345678'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test view of recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a basic recipe"""
        payload = {
            'title': 'Carrot cake',
            'time_minutes': 30,
            'price': 7.0
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipes with tags"""
        tag1 = Tag.objects.create(user=self.user, name='Low calories')
        tag2 = Tag.objects.create(user=self.user, name='Dessert')
        payload = {
            'title': 'Carrot cake',
            'time_minutes': 30,
            'price': 7.0,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipes with ingredients"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Prawns')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'time_minutes': 20,
            'price': 9.0,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with PATCH"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {
            'title': 'Tikka',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti Carbonara',
            'time_minutes': 20,
            'price': 10.0
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_recipes_by_tags(self):
        """Test retrieving filtered list of recipes by tag"""
        recipe1 = sample_recipe(user=self.user, title='Pastel de papas')
        recipe2 = sample_recipe(user=self.user, title='Spaghetti bolognese')
        recipe3 = sample_recipe(user=self.user, title='Ensalada sin carne')
        tag1 = sample_tag(user=self.user, name='tasty')
        tag2 = sample_tag(user=self.user, name='amazing')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        res = self.client.get(RECIPES_URL, {'tags': f'{tag1.id},{tag2.id}'})
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test retrieving filtered list of recipes by ingredient"""
        recipe1 = sample_recipe(user=self.user, title='Hungarian Goulash')
        recipe2 = sample_recipe(user=self.user, title='Spaghetti bolognese')
        recipe3 = sample_recipe(user=self.user, title='Ensalada sin carne')
        ingredient1 = sample_ingredient(user=self.user, name='Goulash')
        ingredient2 = sample_ingredient(user=self.user, name='Minced beef')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class RecipeImageUploadTests(TestCase):
    """Tests for recipe image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@test.com',
            password='user12345678'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_success(self):
        """Test uploading image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as f:
            img = Image.new('RGB', (10, 10))
            img.save(f, format='JPEG')
            f.seek(0)
            res = self.client.post(url, {'image': f}, format='multipart')
        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_failure(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,
                               {'image': 'not-an-image'},
                               format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
