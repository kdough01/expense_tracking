# expense_tracking
Final project for Python Programming. Upload an image of a receipt and have your expenses tracked.

I’d like to create a simple site that tracks a user's expenses by uploading their receipts and categorizing items into groups (groceries, hygiene, health, clothes, etc.).
- Week 4:
  -  Utilize pytessaract to read the receipt from the picture uploaded by the user
  -  Parse the receipt for the store
  -  Parse the receipt for the item and price
- Week 5:
  -  Use either Django or Flask to set up my site
  -  Create an account (username and password) that would be encrypted with a basic cryptographic algorithm
- Week 6:
  -  Categorize each item (if possible I’d want users to be able to create their own categories and move items from one category to another)
-  Week 8:
  -  A user should be able to see their spending at a given store, for a given category, and for a given product over the past month
- Week 9:
  -  Have a chart for spending on a daily/monthly basis for each category


Sources:
- Flask: https://www.youtube.com/watch?v=Z1RJmh_OqeA
- Linking databases in Flask: https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy
- Word classification (using the transformers and pipeline): https://huggingface.co/docs/transformers/main/en/task_summary#zero-shot-text-classification
- Pytesseract to read receipt and parse information: https://pypi.org/project/pytesseract/
- Forms in Flask: https://www.digitalocean.com/community/tutorials/how-to-use-web-forms-in-a-flask-application
- Registering users in Flask: https://www.youtube.com/watch?app=desktop&v=71EU8gnZqZQ
- Preprocessing images in Python: https://www.youtube.com/watch?v=ADV-AjAXHdc