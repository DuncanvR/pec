pec: Project Experiment Controller
===

This neat little program gives an easy way to control the running of experiments.
You can add arbitrary tasks, which are kept in a database.
When run, the output of such a task is copied to the database, for easy review.
This way you can quickly add multiple commands, run them, and check the output later, without worrying data will be lost.
To use it, python2, sqlite3 and its python bindings are needed.

Usage
---
To use pec, invoke it from your favourite shell with <code>./pec.py [options]</code>.
The options and their effects are:

<table>
<tr><td><code>--cli=cmd</code></td>      <td>Passes the given command to the interactive command interpreter and exits.
                                             See the next section for more information on the possible commands;</td></tr>
<tr><td><code>--database=file</code></td><td>The database file to use, the default is ./db.sqlite;</td></tr>
<tr><td><code>--help</code></td>         <td>Shows this help message;</td></tr>
<tr><td><code>--runner</code></td>       <td>Starts the daemon which will run the experiments;</td></tr>
</table>

Each long option <code>--opt</code> also has a short version <code>-o</code>.
To use the short version with an argument, replace the <code>=</code> by a space.
If no option is given, an interactive shell is loaded, in which the commands described next can be executed.

Commands
---
Within the program, the following commands are available.
All these commands can be executed from within the interactive shell, or run from the command line with the <code>--cli=...</code> argument.

<table>
<tr><td><code>add task</code></td>  <td>Adds the given task to the database;</td></tr>
<tr><td><code>execute id</code></td><td>Executes the task(s) with the given id(s);</td></tr>
<tr><td><code>help [cmd]</code></td><td>List the available commands or give detailed help about the given command;</td></tr>
<tr><td><code>list</code></td>      <td>Lists the tasks in the database;</td></tr>
<tr><td><code>remove id</code></td> <td>Removes the task(s) with the given id(s) from the database;</td></tr>
<tr><td><code>reset id</code></td>  <td>Resets the task(s) with the given id(s), clearing its running information;</td></tr>
</table>

The interactive shell supports basic tab-completion for the commands.
Wherever a command expects a task id, multiple ids can be given by separating them by comma's, and ranges can be specified with dashes, e.g. <code>3,4-6,8</code> identifies tasks three, four, five, six and eight.

Examples
---
Lets say we'd want to ping a number of hosts.
We add the tasks by invoking the <code>add</code> command with the task invocation.
Here, we'll ping some interesting host 5 times:

    ./pec.py --cli="add ping -c5 interesting_host_or_IP_address"

When we are done adding tasks, we can run them by invoking the following, which will start the daemon, and run the tasks in order of their ids.
For each task, the daemon will spawn a process to execute it, i.e. call <code>./pec.py -c "execute id"</code>.
This is to ensure that if the daemon is stopped, the output of the running tasks is still collected.

    ./pec.py --runner

Note that only the standard output of a task is stored in the database; error messages are written to the terminal.
Should you want to also catch those messages, append something like <code>2>&1</code> to the command of your task, to redirect stderr to stdout.
For example, the <code>time</code> program, which runs a given command and then prints the time it took, outputs its information on stderr.
So to also keep track of the running time of the ping task added above, we'd call:

    ./pec.py -c "add time (ping -c5 interesting_host_or_IP_address) 2>&1"

Fine-tuning
---
By default, the daemon will run two tasks in parallel.
This behaviour is controlled by the <code>thread\_count</code> field of the <code>pec\_meta</code> table in the database, and currently the only way to change it is by directly manipulating that value.
To change it to for example 8, try:

    sqlite3 db.sqlite "UPDATE pec_meta SET value=8 WHERE name='thread_count';"

