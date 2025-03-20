# CS50Web-Project2-Commerce

## Transcript of project video:

Link to video on YouTube - https://youtu.be/WNCOEolWWfQ

1)
My application has a total of 6 models. In addition to the required models for listings, bids, and comments, I added a model for Categories and one for Watchlist items. Also, I slightly modified the AbstractUser model to add a property that tracks the number of items on the user's watchlist. This enabled me to add a badge in the menu with the number of items being watched that's always visible.

2)
The Create Listing page allows users to create a new listing. It displays an instance of a ListingForm class declared in Views.py. The page uses Bootstrap and some custom CSS for it's appearance. I set up my models so that any listing can have multiple categories. They're indicated by Control-clicking on categories from the list. The reserve price must be a 2-digit decimal. The listing is active by default. The Image file field is optional.

3)
The Active Listings Page is the default page of the application. For each active listing, the title, description, current price and photo are shown. The listings are shown in the order they were created, with the most recent at the top. Clicking on any title will take the user to a more detailed listing for that item.

4)
The listing details page shows all the details about the listing. If the user isn't logged in they'll be shown a message to that effect. The current price and the number of bids that have been made are shown. If the current user is the high bidder at the moment, that information is shown, as well as whether the item is on the user's watchlist or not. There's a button to add the item to the watchlist with a single click, and also, if it's already on the watchlist, there's a button to remove it.

The user can enter a two digit number as a bid. If the bid ISN'T a 2-digit number, or not greater than the current bid, an error message is shown. In the edge case of a bid on an item with no previous bids, the amount may be EQUAL to the starting bid, as well as greater than it.

If the user was the person who created the listing, ther's a button to close the auction. The highest bidder becomes the winner, and the listing is no longer visible in the active listings page. The project specification indicates that the winner should be able to see that they are the winner, but since the page will no longer appear on the active listings page, there would be no easy way to navigate to this page. So, I created a page showing the user all of the auctions they've won, with the ability to see the details page for each listing. The winnings page repourposes the active listings page, but is filtered by closed listings where the user is the high bidder.

Finally, users can see comments about the listing in chronological order, and add their own. 

5)
There's a watchlist page that can be reached from the main menu. Clicking on any item here takes the user to the details page for the item. The entries are in table form, with space for adding a button to remove the item from the watchlist if the app was to be developped further.

6)
The categories page shows a list of all the available categories. Clicking on a category shows a list of the items in that category. This page re-uses the same html file as the active listings page, but filtered by a single category. Clicking on an entry here take the user to the details page. Since I set up a Many-to-many relationship between listings and categories, any particular listing may show up on more that one page listing items in a single category.

7)
I registered all 6 of the models I used in the app site to the admin site for the app, and also added a link to the admin site in the main menu. It's visible only to users allowed on the admin site. I set up string functions on the models so that the entries on the admin site are more informative and easier to find.

