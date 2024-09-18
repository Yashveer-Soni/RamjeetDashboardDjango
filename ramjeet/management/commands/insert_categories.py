# Create a management command file at myapp/management/commands/insert_categories.py

from django.core.management.base import BaseCommand
from ramjeet.models import CategoryMaster, SubCategoryMaster

class Command(BaseCommand):
    help = 'Insert categories and subcategories into the database'

    def handle(self, *args, **kwargs):
        GroceryCategories = {
            "Dals": ["Chana Dal", "Moong Dal", "Tur Dal", "Urad Dal", "Masoor Dal", "Daliya", "Mix Dal"],
            "Pulses": ["Rajma", "Chowli", "Soya Products", "Kabuli Chana", "Chana", "Urad", "Moong", "Masoor", "Vatana", "Other Whole Pulses", "Groundnut"],
            "Dry Fruits": ["Almonds", "Cashews", "Pista", "Dates", "Raisins", "Walnuts", "Apricot", "Mixed Dryfruits", "Charoli", "Makhana", "Anjeer"],
            "Cooking Oil": ["Sunflower Oil", "Groundnut Oil", "Blended Oil", "Rice Bran Oil", "Mustard Oil", "Olive Oil", "Other Oils", "Palm Oil"],
            "Ghee & Vanaspati": ["Cow Ghee", "Ghee", "Vanaspati"],
            "Flours & Grains": ["Atta", "Grains", "Other Flours"],
            "Rice & Rice Products": ["Basmati Rice", "Kolam Rice", "Brown Rice", "Other Rice", "Poha", "Kurmura"],
            "Masala & Spices": ["Whole Spices", "Powdered Spices", "Chilli Powder", "Turmeric Powder", "Coriander Powder", "Cooking Pastes", "Herbs & Seasonings", "Ready Mix Masalas", "Food Essence"],
            "Salt & Sugar & Jaggery": ["Salt", "Sugar", "Sugar Substitutes", "Jaggery"]
        }
        DairyAndBeveragesCategories = {
            "Beverages": ["Tea", "Tea Bags", "Green Tea", "Coffee", "Drink Mixes", "Soft Drinks", "Non-Alcoholic Beers","Juices","Fruit Mixes","Energy Drinks","Squash & Syrups","Concentrates","Soda & Water"],
            "Dairy": ["Milk", "Butter", "Cheese", "Dairy Products", "Dahi", "Yogurt", "Shrikhand", "Paneer"]
        }
        PackagedFoodCategories = {
            "Biscuits & Cookies": ["Cookies", "Glucose Biscuits", "Marie Biscuits", "Salty Biscuits", "Cream Biscuits", "Digestive Biscuits", "Khari & Toasts","Wafer Biscuits","Health Biscuits"],
            "Snacks & Farsans": ["Sev & Mixtures", "Chips & Wafers", "Namkeens", "Snack Bars", "Frozen Snacks", "Popcorn", "Other Snacks"],
            "Breakfast Cereals": ["Flakes", "Oats", "Muesli"],
            "Chocolates & Candies": ["Chocolates", "Candies", "Compound Chocolates","Dark Chocolates"],
            "Ketchup & Sauce": ["Ketchup", "Sauce", "Chutney","Vinegar"],
            "Jams & Spreads": ["Jams", "Spreads", "Honey","Mayonnaise","Dips & Dressings"],
            "Pasta & Noodles": ["Instant Noodles", "Hakka Noodles", "Pasta","Vermicelli"],
            "Ready To Cook": ["Ready Mix", "Popcorn", "Papad"],
            "Gourmet Food": ["Beverages", "Biscuits & Chocolates", "Ketchup & Sauces","Noodles & Pasta","Dark Chocolates"],
            "Health Food": ["Honey", "Chyawanprash", "Sugar Substitutes","Other Healthy Alternatives"],
            "Soups": [""],
            "Mukhwas": [""],
        }

        HomeAndKitchenCategories = {
            "Detergent & Fabric Care": ["Liquid Detergent", "Detergent Powder", "Detergent Bar","Fabric Care"],
            "Cleaners": ["Floor Cleaners", "Toilet Cleaners", "Other Cleaners"],
            "Utensil Cleaners": ["Dishwash Liquids", "Dishwash Bars", "Sponges & Scrubs","More Cleaners"],
            "Freshener & Repellents": ["Air Fresheners", "Repellents", "Mosquito Bat","Mosquito Net"],
            "Disinfectants": ["Disinfectant Liquid & Spray"],
            "Tissue Paper & Napkins": ["Aluminium Foils", "Face Tissues", "Garbage Bags","Kitchen Tissues","Tissue Paper & Napkins","Toilet Paper"],
            "Pooja Needs": ["Pooja Oil", "Camphor & Kapur", "Agarbatti & Dhoop","Diya","Chowki (Paat/Chaurang)","Agarbatti Stand","Festive Candles"],
            "Tissue Paper & Napkins": ["Aluminium Foils", "Face Tissues", "Garbage Bags","Kitchen Tissues","Tissue Paper & Napkins","Toilet Paper"],
        }
        PersonalCareCategories = {
            "Skin Care": ["Soaps", "Creams & Lotions", "Face Care","Talcum Powder","Shower Gels","Sunscreen","Lip Care","Skin Protection"],
            "Face Care": ["Face Wash", "Face Scrub", "Face Cream","Face Tissues","Face Mask","Face Serum","Compact","Foundation","Primer","BB & CC Cream","Makeup Remover","Other Face Care"],
            "Hair Care": ["Hair Oil", "Hair Shampoos", "Hair Conditioners","Hair Colour","Hair Gel & Cream","Hair Appliances","Hair Comb","Hair Serum"],
            "Oral Care": ["Toothpaste", "Mouthwash", "Toothbrush"],
        }

        for category_name, subcategory_names in GroceryCategories.items():
            category, created = CategoryMaster.objects.get_or_create(category_name=category_name, parent_cat_id=1)  # Adjust parent_cat_id if needed
            for subcategory_name in subcategory_names:
                SubCategoryMaster.objects.get_or_create(category=category, sub_category_name=subcategory_name)

        for category_name, subcategory_names in DairyAndBeveragesCategories.items():
            category, created = CategoryMaster.objects.get_or_create(category_name=category_name, parent_cat_id=2)  # Adjust parent_cat_id if needed
            for subcategory_name in subcategory_names:
                SubCategoryMaster.objects.get_or_create(category=category, sub_category_name=subcategory_name)
                
        for category_name, subcategory_names in PackagedFoodCategories.items():
            category, created = CategoryMaster.objects.get_or_create(category_name=category_name, parent_cat_id=3)  # Adjust parent_cat_id if needed
            for subcategory_name in subcategory_names:
              SubCategoryMaster.objects.get_or_create(category=category, sub_category_name=subcategory_name)

        for category_name, subcategory_names in HomeAndKitchenCategories.items():
            category, created = CategoryMaster.objects.get_or_create(category_name=category_name, parent_cat_id=4)  # Adjust parent_cat_id if needed
            for subcategory_name in subcategory_names:
                SubCategoryMaster.objects.get_or_create(category=category, sub_category_name=subcategory_name)

        for category_name, subcategory_names in PersonalCareCategories.items():
            category, created = CategoryMaster.objects.get_or_create(category_name=category_name, parent_cat_id=5)  # Adjust parent_cat_id if needed
            for subcategory_name in subcategory_names:
                SubCategoryMaster.objects.get_or_create(category=category, sub_category_name=subcategory_name)
        
        self.stdout.write(self.style.SUCCESS('Successfully inserted categories and subcategories'))
