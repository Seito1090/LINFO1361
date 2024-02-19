\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{../assignment}[2010/09/14 v0.2 ingi2261 assignment class]

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Options

\gdef\@docname{Assignment}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Class loading
\LoadClass[11pt,oneside,a4paper]{article}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[math]{iwona}
\RequirePackage[scaled=0.8]{beramono}
\RequirePackage{amsmath,amsfonts,amssymb,braket}
\RequirePackage{array}
\RequirePackage[hmargin=3cm,vmargin=2cm,includehead,includefoot]{geometry}
\RequirePackage{graphicx}
\RequirePackage{float,caption}
\RequirePackage{multicol,multirow}
\RequirePackage{chngpage}
\RequirePackage{listings}
\RequirePackage{enumitem}
\RequirePackage{subcaption}
\RequirePackage{caption}

\graphicspath{{},{../images/}}
\pdfimageresolution 150

\@tempdima=\parindent
\RequirePackage{parskip}
\parindent=\@tempdima
%\RequirePackage{indentfirst}

\RequirePackage{tikz}
\RequirePackage{tikz-qtree}
\usetikzlibrary{calc,positioning,shapes,arrows}
\RequirePackage[tikz]{bclogo}

\RequirePackage[pdftex,colorlinks=false,pdfborder={0 0 0}]{hyperref}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Meta-data
\newcommand*\assignment[1]{\gdef\@assignment{#1}}
\gdef\@assignment{\ClassError{assignment}{No assignment number specified}{}}

\newcommand*{\captionsource}[2]{%
  \caption[{#1}]{%
    #1%
    \\\hspace{\linewidth}%
    \textbf{Source:} #2%
  }%
}

\newcommand*\due[1]{\gdef\@due{#1}}
\gdef\@due{\ClassError{assignment}{No due date specified}{}}

\newcommand*\guideline[1]{\g@addto@macro\@addguidelines{\item #1}}
\gdef\@addguidelines{}

\author{Fran\c cois Aubry \and Gael Aglin \and Yves Deville}

\AtBeginDocument
  {\bgroup
   \def\and{, }
   \hypersetup
     {pdftitle={LINGI2261 \@docname\ \@assignment: \@title},
      pdfauthor={\@author}}
   \egroup}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Style

% title
\def\@maketitle%
  {\newpage
   \begin{center}%
   \let \footnote \thanks
     {\Large\bf LINGI2261: Artificial Intelligence \\
      \@docname\ \@assignment: \@title \par}%
     \def\and{\unskip, }
     \@author\\
     \@date
   \end{center}%
   \par
   \vskip 1.5em
   \begin{guidelines}
   \item This assignment is due on \emph{\bf\@due}.
   \@addguidelines
   \item \emph{No delay} will be tolerated.
   \item Not making a \emph{running implementation} in \emph{Python 3} 
	     able to solve (some
         instances of) the problem is equivalent to fail. Writing some lines of
         code is easy but writing a correct program is much more difficult.
   \item \emph{Document} your source code (at least the difficult or more
         technical parts of your programs). Python docstrings for important
         classes, methods and functions are also welcome.
   \item Indicate clearly in your report if you have \emph{bugs} or problems in
         your program. The online submission system will discover them anyway.
   \item Copying code or answers from other groups (or from the internet) is strictly
         forbidden. Each source of inspiration must be clearly indicated. The
         consequences of \emph{plagiarism} is \emph{0/20 for all assignments}.
   \item Source code shall be submitted on the online \emph{INGInious} system. 
   		 Only programs submitted via this procedure will be graded. No report or program
         sent by email will be accepted.
   \item Respect carefully the \emph{specifications} given for your program
         (arguments, input/output format, etc.) as the program testing system is \emph{fully
         automated}.
   \end{guidelines}}

% header boxes
\newenvironment{guidelines}
  {\par
   \begin{bclogo}[couleur=red!10,arrondi=0.5,noborder,marge=8,logo=\bcattention,
                  couleurBarre=red!90!black]
                 { Guidelines}
   \renewcommand\emph[1]{{\color{red!90!black}\em ##1}}
   \begin{itemize}}
  {\end{itemize}\end{bclogo}\par}
\newenvironment{deliverables}
  {\par
   \begin{bclogo}[couleur=yellow!20,arrondi=0.5,noborder,marge=8,logo=\bcinfo,
                  couleurBarre=yellow!90!black]
                 { Deliverables}
   \newcommand\PaperReport
     {\item The answers to all the questions in a report \textbf{on INGInious. Do not forget to put your group number on the front page as 
     well as the INGInious id of both group members.}}
   \newenvironment{Files}
     {\item The following files are to be submitted on \emph{INGInious} inside the \emph{Assignment \@assignment} task(s):
            \begin{itemize}}
     {\end{itemize}}
   \begin{itemize}}
  {\end{itemize}\end{bclogo}\par}

% code
\DeclareTextFontCommand{\file}{\tt}
\lstset{language=Python,
	basicstyle=\ttfamily,
	keywordstyle={\bfseries\color{blue!50!black}},
	commentstyle={\color{black!75}},
	showstringspaces=false,
	keepspaces=true,
	tabsize=4,
	columns=fullflexible}
\newenvironment{code}[1][Code]
  {\par\begin{bclogo}[noborder,logo=\bccrayon]{ #1}}
  {\end{bclogo}\par}

% questions
\newenvironment{questions}
  {\par
   \begin{bclogo}[couleur=blue!10,arrondi=0.5,noborder,marge=8,logo=\bcplume,
                  couleurBarre=blue!50!black]
                 { Questions}
   \let\enit@resume@enumerate\ass@qresume
   \begin{enumerate}}
  {\end{enumerate}
   \global\let\ass@qresume\enit@resume@enumerate
   \end{bclogo}\par}


%important
\newenvironment{important}
  {\par
   \begin{bclogo}[couleur=red!10,arrondi=0.5,noborder,marge=8,logo=\bcattention,
                  couleurBarre=red!90!black]
                 { Important}
   \renewcommand\emph[1]{{\color{red!90!black}\em ##1}}
   \begin{itemize}}
  {\end{itemize}\end{bclogo}\par}


% floats
\restylefloat{figure}
\floatevery{figure}{\centering}
\floatplacement{figure}{htbp}

\restylefloat{table}
\floatevery{table}{\centering}
\floatplacement{table}{htbp}

\captionsetup{margin=2cm,font={small}}

% autoref names
\let\subsectionautorefname\sectionautorefname
\let\subsubsectionautorefname\sectionautorefname

\newcommand{\myref}[2]{\hyperref[#2]{#1~\ref{#2}}}
