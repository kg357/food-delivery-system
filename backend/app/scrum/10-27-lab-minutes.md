# Scrum Meeting Minutes

Date: 2026-10-27
Time: 2-4pm
Location: ART 214
Meeting Type: Lab Meeting
Minute Taker: Trinity

## Attendees
- Gillpreet (Gill-7)
- Kiran (kg357)
- Trinity (trinitybell19)

## Meeting Goals
- Discuss the workflow for Milestone 2
- Add the pull trigger

## Discussion
- Dividing up Milestone 2 into broad User Stories
- How to handle user authentication
- Assigning design improvements

### Decisions Made
- We will implement encrypted passwords straight away to prevent future revision
- User stories chosen: 
    US A1: Customer account creation (registering a customer with a unique ID, name, address, payment methods, and an encrypted password)
    US A2: Customer account modification
    US A3: Customer account authentication (for creation, logging in, and modifying the account, using the encrypted password)
    US B1: Customer cart creation (persistent so they can continue browsing without immediately checking out)
    US B2: Customer cart modification (removing items, increasing or decreasing the quantity of items, clearing the cart)
    US C1: Customer checkout (validates the customer and items, creates a persistent order, clears the cart after the order is placed, and returns the created order)
    US C2: Administrative order management (retrieving an order, filtering orders)
    Notes: Orders will have an identification for their historical order. The customer must be repeatedly validated through each stage. Their personal information (payment information, password, address) should be encrypted. Tests and frontend must be implemented for each User Story.
- Possible design improvements:
    Move menu item UUID creation to identifiers.py
    Improve the visual consistency and appeal of the frontend (can be divided into multiple improvements)
    

## Next Meeting
Date: 11-03 (lab meeting)
Time: 2-4pm

### Goals For Next Meeting: 
- Finish dividing up the work for Milestone 2 and assign team members to complete it 
