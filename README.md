# deph: kill Ceph

⚠️**Dangerous Code Ahead!**⚠️

This repo contains scripts to trigger [Ceph MDS deadlocks](https://tracker.ceph.com/issues/65607), on a Slurm cluster. These are useful for reproducing the deadlock problem on demaind, in order to obtain debug logs, find the deadlocking code in the Slurm MDS, and fix whatever is causing the deadlock.

## Using for Evil

The malicious applications of these scripts are expected to be limited: if you repeatedly lock up directories on your institution's Ceph cluster without permission, you are likely to have your access revoked. Nonetheless, consider this your legally required reminder that **you should not deliberately denial-of-service attack Ceph clusters**, with this tool or otherwise.

## Using for Good

You can submit a job with:

```
sbatch --partition=medium --time=01:00:00 --wait --output=output-ceph.txt file-deph.sh lock 10 /private/groups/patenlab/anovak/trash/testdir
```

This allocates a 1 hour time limit, and tries to run for 10 seconds, vigorously locking and unlocking and creating and deleting a file in that directory, using code [adapted from Toil 6.1](https://github.com/DataBiosphere/toil/blob/3f9cba3766e52866ea80d0934498f8c8f3129c3f/src/toil/lib/threading.py#L359-L470).

If it "works", the batch will not actually finish in 10 seconds, and instead will hang. Attempts to `ls /private/groups/patenlab/anovak/trash/testdir` will also hang. At this point, there should be a deadlock in one of your Ceph cluster's MDS servers; restarting the server process should restore access to the broken directory.

You can `scancel` the Slurm batch, but the directory will remain stuck.

The Slurm batch script, `file-deph.sh`, runs the `bang-on-files.py` script on 10 nodes, with 4 instances of the script per node. It may be possible to create the problem with fewer nodes or processes.

I *think* it will lock up every time, but I'm not going to test it repeatedly before our Ceph admin gets in to work for the day. Bad things might happen to the cluster overall if many MDS processes or threads are deadlocked.

## Help I Broke Something

Restarting the Ceph MDS(es) *should* restore your filesystem to full functionality. If it doesn't, I unfortunately can't help.
