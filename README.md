# NBA live results: always-on updater

Every 5 minutes on game nights, GitHub reads ESPN's box scores and saves them to the NBA Plays board,
so results show for everyone (guests included) with nobody's computer on.

Files:
- `espn_live.py`: reads ESPN, writes `live.json` only while a game is live or just finished.
- `save.sh`: runs Claude Code (signed in as Dylan) to save `live.json` to the board's `live/stats`.
  It leaves results alone if someone clicked Remove results that night.
- `.github/workflows/nba-live.yml`: the schedule (every 5 minutes, 11 AM to 3 AM New York time).

## One-time setup

1. **Make the sign-in key.** In Terminal run `claude setup-token`, sign in with the work account, and copy the
   key it prints. Treat it like a password.
2. **Make a GitHub repository.** Go to github.com/new, name it `nba-live-results`, choose **Public**
   (unlimited free run time; nothing secret is in these files), and create it.
3. **Upload the files.** In the repository click **Add file > Upload files** and drag in `espn_live.py`,
   `save.sh`, `README.md` and the `.github` folder (in Finder press Cmd+Shift+. to show it). Commit.
4. **Add two secrets.** Settings > Secrets and variables > Actions > New repository secret:
   - `CLAUDE_CODE_OAUTH_TOKEN`: the key from step 1
   - `BOARD_URL`: start with the TEST board, `https://claude.ai/artifact/QMnbSSPMB4wknFB2auXuWA`
5. **Test it.** Actions tab > NBA live results > Run workflow, tick "Save even if no game is live", Run.
   A green check means it saved. Then switch `BOARD_URL` to the real board,
   `https://claude.ai/artifact/DNoHVnpauj1XmiEqD6rkme`.

To stop it: Actions tab > NBA live results > ... > Disable workflow.
