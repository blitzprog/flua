from flua.Tools.IDE.Environment.BaseEnvironment import *

class CPPEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir, action):
		BaseEnvironment.__init__(self, action)
		
		self.name = "C++"
		self.rootDir = rootDir
		self.fileExtensions = {".cpp", ".cxx", ".c", ".hpp", ".h"}
		self.standardFileExtension = ".cpp"
		self.singleLineCommentIndicators = {"//"}
		self.preprocessorIndicators = {"#"}
		self.selfReferences = {"this"}
		
		self.autoCompleteKeywords = {
			'and', 'asm', 'assert',
			'break',
			'class', 'continue', 'const', 'case', 'catch',
			'default', 'delete',
			'elif', 'else', 'extern', 'extends', 'enum',
			'for', 'false',
			'if', 'inline', 'include',
			'long',
			'not', 'null', 'namespace', 'new',
			'or', 'operator',
			'private', 'public',
			'return',
			'sizeof', 'switch', 'struct',
			'try', 'typename', 'typedef', 'template', 'throw', 'true',
			'until',
			'virtual', 'volatile',
			'while',
		}
		self.highlightKeywords = self.autoCompleteKeywords
		
		self.internalDataTypes = {
			# C
			'char', 'bool', 'void', 'int', 'float', 'double', 'short', 'unsigned',
		}
		
		self.internalFunctions = {
			"isalnum",
			"isalpha",
			"iscntrl",
			"isdigit",
			"isgraph",
			"islower",
			"isprint",
			"ispunct",
			"isspace",
			"isupper",
			"isxdigit",
			"toupper",
			"tolower",
			"errno",
			"setlocale",
			"acos",
			"asin",
			"atan",
			"atan2",
			"ceil",
			"cos",
			"cosh",
			"exp",
			"fabs",
			"floor",
			"fmod",
			"frexp",
			"ldexp",
			"log",
			"log10",
			"modf",
			"pow",
			"sin",
			"sinh",
			"sqrt",
			"tan",
			"tanh",
			"setjmp",
			"longjmp",
			"signal",
			"raise",
			"va_start",
			"va_arg",
			"va_end",
			"clearerr",
			"fclose",
			"feof",
			"fflush",
			"fgetc",
			"fgetpos",
			"fgets",
			"fopen",
			"fprintf",
			"fputc",
			"fputs",
			"fread",
			"freopen",
			"fscanf",
			"fseek",
			"fsetpos",
			"ftell",
			"fwrite",
			"getc",
			"getchar",
			"gets",
			"perror",
			"printf",
			"putchar",
			"puts",
			"remove",
			"rewind",
			"scanf",
			"setbuf",
			"setvbuf",
			"sprintf",
			"sscanf",
			"tmpfile",
			"tmpnam",
			"ungetc",
			"vfprintf",
			"vprintf",
			"vsprintf",
			"abort",
			"abs",
			"atexit",
			"atof",
			"atoi",
			"atol",
			"bsearch",
			"calloc",
			"div",
			"exit",
			"getenv",
			"free",
			"labs",
			"ldiv",
			"malloc",
			"mblen",
			"mbstowcs",
			"mbtowc",
			"qsort",
			"rand",
			"realloc",
			"strtod",
			"strtol",
			"strtoul",
			"srand",
			"system",
			"wctomb",
			"wcstombs",
			"memchr",
			"memcmp",
			"memcpy",
			"memmove",
			"memset",
			"strcat",
			"strchr",
			"strcmp",
			"strcoll",
			"strcpy",
			"strcspn",
			"strerror",
			"strlen",
			"strncat",
			"strncmp",
			"strncpy",
			"strpbrk",
			"strrchr",
			"strspn",
			"strstr",
			"strtok",
			"strxfrm",
			"asctime",
			"clock",
			"ctime",
			"difftime",
			"gmtime",
			"localtime",
			"mktime",
			"strftime",
			"time",
			"opendir",
			"closedir",
			"readdir",
			"rewinddir",
			"scandir",
			"seekdir",
			"telldir",
			"access",
			"alarm",
			"chdir",
			"chown",
			"close",
			"chroot",
			"ctermid",
			"cuserid",
			"dup",
			"dup2",
			"execl",
			"execle",
			"execlp",
			"execv",
			"execve",
			"execvp",
			"fchdir",
			"fork",
			"fpathconf",
			"getegid",
			"geteuid",
			"gethostname",
			"getop",
			"getgid",
			"getgroups",
			"getlogin",
			"getpgrp",
			"getpid",
			"getppi",
			"getuid",
			"isatty",
			"link",
			"lseek",
			"mkdir",
			"open",
			"pathconf",
			"pause",
			"pipe",
			"read",
			"rename",
			"rmdir",
			"setgid",
			"setpgid",
			"setsid",
			"setuid",
			"sleep",
			"sysconf",
			"tcgetpgrp",
			"tcsetpgrp",
			"ttyname",
			"unlink",
			"write",
			"clrscr",
			"getch",
			"getche",
			"direnth",
			"statfs",
			"unistdh",
			"endpwent",
			"fgetpwent",
			"getpw",
			"getpwent",
			"getpwnam",
			"getpwuid",
			"getuidx",
			"putpwent",
			"pclose",
			"popen",
			"putenv",
			"setenv",
			"setpwent",
			"setreuid",
			"stat",
			"uname",
			"unsetenv",
			"setuidx",
			"setegid",
			"setrgid",
			"seteuid",
			"setruid",
			"getruid",
			"sizeof",
			"clrscr",
			"convesc",
			"basename",
			"printenv",
			"lenstr",
			"reverse",
		}
		
		#self.specialKeywords = {
		#	# GLSL
		#	'in', 'out', 'inout',
		#	'attribute', 'uniform', 'varying',
		#}
