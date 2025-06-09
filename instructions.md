We're going to work on a specific user story that will incorporate many things. 
Keep in mind we are trying to keep this a simple but extensible framework to implement
many kinds of MUDs, although we'll stick with stars without number.

Please create a checklist of things we will need to successfully code this user story:

We'll assume a player is already logged in.

1.  The user walks into a room that is "dark" so they can't see anything by default.
1.a The room will just look like "It's too dark to see"
2. The user has night vision goggles that they have equipped on their head.  The 'use goggles' to turn them on.  When the now "look", the room description shows in green. 
3.  There is a "Thug" NPC in the room.
4.  The user uses the skill "intimidate" that rolls against charisma stat.
5. On success the Thug will then become my unwilling follower.
6.  User then "order thug airlock" where the thug goes out an airlock exit.
7.  User "press red button" which will open the airlock, which sends all the contents included "Thug" out into space.
8.  The thug will eventually die because they aren't able to breathe in the environment. 

Think hard about all of the systems that neeed to be in place to support this use case.  Things like room environments, opposed skill checks, etc. Create a requirements checkist with main items and subitems necessary.                                                     │