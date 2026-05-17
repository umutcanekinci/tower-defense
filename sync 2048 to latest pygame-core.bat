git submodule update --remote src/pygame_core
git add src/pygame_core

pause

/*
  1. cd src/pygame_core
  2. git add . && git commit -m "..."     ← captures the actual code
  3. git push origin main                 ← makes it available to everyone
  4. cd ..                                 ← back to TD root
  5. git add src/pygame_core              ← bumps TD's gitlink to the new commit
  6. git commit -m "Bump pygame-core"     ← records that bump in TD
  7. git push                              ← (optional)

*/