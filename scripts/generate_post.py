"""
CookingMadeEasy Auto Post Generator
Generates SEO-optimized cooking articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High-traffic cooking keyword categories
TOPIC_POOLS = {
    "easy_recipes": [
        "15-Minute Dinner Recipes for Busy Weeknights",
        "{number} Easy One-Pot Meals Anyone Can Make",
        "Quick and Easy Pasta Recipes Ready in Under 20 Minutes",
        "Simple Sheet Pan Dinners for the Whole Family",
        "{number} No-Cook Meals Perfect for Hot Summer Days",
        "Easy Slow Cooker Recipes You Can Set and Forget",
        "5-Ingredient Dinners That Taste Amazing",
        "{number} Easy Recipes for Beginners Who Can't Cook",
        "Quick Stir-Fry Recipes Ready in {number} Minutes",
        "Easy Comfort Food Recipes for Cozy Nights In",
    ],
    "meal_prep": [
        "Meal Prep for Beginners: A Complete Guide for {year}",
        "How to Meal Prep for the Entire Week in 2 Hours",
        "{number} Meal Prep Ideas That Won't Get Boring",
        "Freezer-Friendly Meals You Can Prep in Advance",
        "Meal Prep Breakfast Ideas to Save Your Mornings",
        "How to Meal Prep on a Budget in {year}",
        "Healthy Meal Prep Lunches for Work",
        "{number} Meal Prep Containers and Tools You Need",
        "Sunday Meal Prep Routine That Saves Hours Each Week",
        "Meal Prep Snacks to Keep You Full All Day",
    ],
    "baking": [
        "Easy Baking Recipes for Absolute Beginners",
        "How to Bake the Perfect Chocolate Chip Cookies",
        "Simple Banana Bread Recipe That Never Fails",
        "Homemade Bread Baking Guide for Beginners",
        "{number} Easy Cake Recipes You Can Make at Home",
        "How to Make Fluffy Pancakes from Scratch",
        "Best Muffin Recipes for Breakfast and Snacks",
        "No-Bake Desserts That Taste Incredible",
        "Easy Pie Recipes for Every Season",
        "How to Make Homemade Pizza Dough Like a Pro",
    ],
    "healthy_cooking": [
        "Healthy Dinner Ideas That Actually Taste Good",
        "{number} High-Protein Meals for Muscle Building",
        "Low-Carb Recipes That Don't Feel Like a Diet",
        "How to Cook Vegetables So They Actually Taste Delicious",
        "Healthy Smoothie Recipes for Every Goal",
        "Mediterranean Diet Recipes for Beginners",
        "Quick Healthy Breakfast Ideas for Busy Mornings",
        "Plant-Based Meals Even Meat Lovers Will Enjoy",
        "Healthy Snack Ideas to Curb Your Cravings",
        "How to Make Healthy Salads That Fill You Up",
    ],
    "kitchen_tips": [
        "Best Kitchen Gadgets Worth Buying in {year}",
        "How to Cook Perfect Rice Every Single Time",
        "{number} Cooking Mistakes That Ruin Your Food",
        "Essential Knife Skills Every Home Cook Needs",
        "How to Season a Cast Iron Skillet Properly",
        "Kitchen Organization Tips to Save Time and Space",
        "How to Read a Recipe Like a Professional Chef",
        "{number} Cooking Hacks That Will Change Your Life",
        "How to Store Food Properly to Reduce Waste",
        "The Best Cooking Oils and When to Use Each One",
    ],
    "budget_meals": [
        "Budget Meals Under $5 Per Serving",
        "How to Feed a Family of Four for Under $50 a Week",
        "{number} Cheap and Healthy Meals for College Students",
        "Budget-Friendly Grocery List for a Week of Meals",
        "How to Cook Delicious Meals with Pantry Staples",
        "Rice and Beans Recipes That Are Anything But Boring",
        "Cheap Dinner Ideas When You're Broke",
        "How to Eat Well on a Tight Budget in {year}",
        "{number} Dollar Store Meals That Actually Taste Great",
        "Budget Meal Planning Tips That Save Hundreds Monthly",
    ],
    "international": [
        "Easy Italian Recipes You Can Make at Home",
        "Beginner's Guide to Thai Cooking",
        "How to Make Authentic Mexican Tacos at Home",
        "Simple Japanese Recipes for Home Cooks",
        "Easy Indian Curry Recipes for Beginners",
        "Korean Cooking 101: {number} Recipes to Get Started",
        "Classic French Recipes Made Simple",
        "Easy Chinese Takeout Recipes to Make at Home",
        "Mediterranean Recipes That Transport You Abroad",
        "How to Make Middle Eastern Favorites at Home",
    ],
}

SYSTEM_PROMPT = """You are an expert food writer and home cook for a blog called CookingMadeEasy.
Write SEO-optimized, practical, and engaging cooking blog posts.

Rules:
- Write in a warm, encouraging, and conversational tone
- Use short paragraphs (2-3 sentences max)
- Include practical, step-by-step instructions where relevant
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion or encouragement to try the recipe
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are an experienced home cook sharing your best tips
- Include specific measurements, times, and temperatures
- Mention flavor descriptions and sensory details
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        # If all attempts hit duplicates, add a random suffix
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Easy recipes and cooking tips for home cooks of every skill level."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename


if __name__ == '__main__':
    filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
