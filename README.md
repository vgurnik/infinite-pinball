# Infinite Pinball
Maybe this shall be a game someday

build:
```bash
pip install pygame pymunk pyinstaller
pyinstaller main.spec
```

### TODO:
#### 1 ✔
- [x] Add build mode
  - [x] Separate field and UI
- [x] Actually add card effects
  - [x] Add event system
- [x] Add pack opening
- [x] Add descriptions (context)
- [x] Add preferences
#### 2
- [x] Finish texturing the field
  - [x] Resolution rescale
- [ ] Texturize GUI
  - [x] Separate buttons finally
- [ ] Texturize cards
- [ ] Add active effects visualization
#### 3
- [ ] Add saves
- [ ] Add more card-object-effect options
  - [ ] Implement rarity
  - [ ] Implement multiple effects per card
  - [ ] Implement card id to allow to affect effects
#### 4
- [ ] Balance scoring
  - [x] Implement effect cooldown
  - [ ] Add building restrictions
- [ ] Balance economy
  - [x] Implement shop rerolls
- [ ] Finish starting field
#### 5
- [ ] Implement special effects (combos)
- [ ] Add starting field options
- [ ] Add unlockables (fields, cards, difficulties)
- [ ] ***Add even more card-object-effect options***
#### ?
- [ ] Add sounds
- [x] Pack the app conveniently
- [ ] Add localization
- [ ] Add SCALED resolution maybe, works strangely