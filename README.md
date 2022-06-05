# Binder Organizer
Binder Organizer (alias Help Your Back) is a python script aimed to solve a simple task that will eventually help your back.

## Problem
Let's say you go to school and you carry all your day's schedule assignments. Imagine you have 100 different assignments (ex: Algebra, Geometry, Particles, ...).

You may organize yourself with a binder and put all the chapters of all of the assignments in that binder. (ex: Algebra I, Algebra II, Algebra III, Geometry I, Particles I, ...)

**What's the best way to organize yourself with binders in order to help your back and carry the least amount of weight possible?**

### Solutions
- Only put the **current chapters you're working on** (ex: Algebra III instead of Algebra I, Algebra II and Algebra III). 
- **Distribute the different assignments in different binders** and only carry the needed binders For example, you have 50 assignments in Binder_1 [Algebra, Geometry, ...], and 50 others in Binder_2 [Particles, ...]. If one day you're only attending Algebra class, you won't need to carry 99 useless chapters with you, you will only need to carry 49!

Here comes the simple question: _**"What's the best way to distribute all of the assignments in ß different binders, so that you carry on average the least amount of weight possible?"**_

This python script aims to answer that question.

## Configuration

The configuration of this program is stored in configuration.cfg. There are multiple categories that will have to be filled-in.

Note : Be consistent with the measurement units and the assignment names in all the configuration.

### Measuring the weight per chapter of every assignment
Each assignment could have a different quantity of paper, and thus a different weight. I recommend spending some time measuring in order to be more accurate because this program will give the absolute best solution to the problem.

I implemented two ways in order to measure the weight per assignment:

- Measuring the weight of each chapter of every assignment (ex: 0.5kg) (tedious)
- Measuring the paper width per chapter (ex: 1cm) of every assignment and then measuring the weight per every cm of paper (ex: 0.5 kg/cm)(less precise)(less tedious)

You must only apply one way of measurement.

#### [PAPER_WEIGHT_PER_ASSIGNMENT]
This category will contain the weight per chapter of every assignment.

It will be written in the following way:
(assignment code) = (weight)

Note: each assignment must be specified in a new line.

Ex in kg:
```
ALGEBRA = 0.5
MATH = 1.5
```

#### [PAPER_WIDTH_PER_ASSIGNMENT]
This category contains the paper width per chapter of every assignment.

Il will be written in the following way:
(assignment code) = (width)

Note: each assignment must be specified in a new line.

Ex in cm:
```
ALGEBRA = 1
MATH = 3
```

### Schedule
In order to calculate the average carried weight with different assignment combinations, the program must know which assignments go on which hour and when you can change your backpack's contents.
 
#### [ASSIGNMENTS_PER_DAY_WEEK1]
This category contains the week's schedule.

Each day must be expressed on a new line in the following way:
```
(day of the week) = (Assignment code 1),(assignment code 2) (space = binder change) (Assignment code ...)
```

Each space means a break where you can change your books and binders.

Ex:
```
MONDAY = ALGEBRA,MATH GEOMETRY,GEO,ENG FRENCH,SPANISH
```

### Writing multiple weeks
If your schedule changes depending on the week, you can write that down with the following syntax:

```
[ASSIGNMENTS_PER_DAY_WEEK1]
MONDAY = ALGEBRA,MATH
TUESDAY = ALGEBRA,GEOMETRY SPANISH

[ASSIGNMENTS_PER_DAY_WEEK2]
MONDAY = ALGEBRA,SPANISH
TUESDAY = GEOMETRY,FRENCH ALGEBRA
WEDNESDAY = SPANISH FRENCH

[ASSIGNMENTS_PER_DAY_WEEK3]
TUESDAY = MATH
THURSDAY = ENGLISH

...
```

### [GENERAL]
- EMPTY_BINDER_WEIGHT: The weight of an empty binder (Ex in kg: 0.4)
- WEIGHT_PER_HEIGHT_UNIT: In the case you used the width measurement option, you must include the ratio between the weight and the width of the binder's content. (Ex in kg / cm: 0.3)

## Best combination for n binders
```python
back_helper = BackHelper()

best_2_binder_combination = back_helper.get_best_combination_for_n_binders(2)
```


## Absolute best combination?
Running the program, I noticed something quite strange:
- best combination with 5 binders: [['ENG' , 'HGE' ], [ 'FR' ], [ 'ESP' , 'CAT' , 'EMC' ], [ 'HGF' , 'SPC' ], [ 'SES' ]]
- best combination with 6 binders: [ [ 'ENG' , 'HGE' ], [ 'FR' ], [ 'ESP' , 'CAT' , 'EMC' ], [ 'HGF' , 'SPC' ], [ 'SES' ], [ ] ]

Huh? They actually are the same combination... Does the absolute best combination only have 5 binders?!

We may think that the best combination is the one where each assignment is on a different binder, but test tells us the opposite.

Some assignments are so light-weight, that it would be heavier carrying the weight of an empty binder + the weight of the assignment than carrying the weight of other assignments too!

```python
back_helper = BackHelper()

absolute_best_combination = back_helper.get_absolute_best_combination()
```