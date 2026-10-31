#ifndef PS2DISC_PROBE_H
#define PS2DISC_PROBE_H
#include <stdatomic.h>
#include <stdint.h>
#define PROBE_LOG_LINES 512
#define PROBE_LINE_LENGTH 192
extern char probe_lines[PROBE_LOG_LINES][PROBE_LINE_LENGTH];
extern atomic_uint probe_line_count;
extern atomic_int probe_done, probe_stop, probe_log_failed, probe_timed_out;
extern atomic_uint_fast64_t probe_deadline;
extern atomic_uint_fast64_t probe_stage_deadline;
/* Published before worker creation: 0 all, 1 files, 2 storage, 3 v2 baseline. */
extern unsigned probe_selection;
uint64_t probe_now(void);
void probe_worker(void *unused);
#endif
