<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:param name="branchName" required="no" as="xs:string"/>
    <xsl:param name="qaBuildId" required="no" as="xs:string"/>
    <xsl:param name="qaBuildTime" required="no" as="xs:string"/>
    <xsl:param name="packagerBuildId" required="no" as="xs:string"/>
    <xsl:output method="html" indent="yes" encoding="US-ASCII"
                doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>
    <xsl:decimal-format decimal-separator="." grouping-separator=","/>

    <xsl:template match="testsuites">
        <html>
            <head>
                <title>Teradata Quality Check</title>
                <style type="text/css">
                    h1 {
                    font-family: verdana,arial,sans-serif;
                    font-size:15px;
                    }
                    h2, h3 {
                    font-family: verdana,arial,sans-serif;
                    font-size:13px;
                    }
                    p {
                    font-family: verdana,arial,sans-serif;
                    font-size:11px;
                    }
                    table {
                    font-family: verdana,arial,sans-serif;
                    font-size:11px;
                    color:#333333;
                    border-width: 1px;
                    border-color: #ccc;
                    border-collapse: collapse;
                    border-top-left-radius: 2em;
                    }
                    table th {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #ccc;
                    background: -webkit-linear-gradient(top, #FFE784, #FFCC00);
                    }
                    table td {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #ccc;
                    background-color: #ffffff;
                    }
                    label {
                    padding-right: 20px;
                    vertical-align: top;
                    }
                    .Warning {
                    font-weight:bold; color:orange;
                    }
                    .Failure {
                    font-weight:bold; color:red;
                    }
                </style>
                <script>
                function toggleRows(checkBoxId, className) {
                    if (document.getElementById(checkBoxId).checked) {
                        showRows(className);
                    }
                    else {
                        hideRows(className);
                    }
                }
                function hideRows(className) {
                    var rows = document.getElementsByClassName(className), i;
                    for (i = 0; i &lt; rows.length; ++i) {
                      rows[i].style.display = 'none';
                    }
                }
                function showRows(className) {
                    var rows = document.getElementsByClassName(className), i;
                    for (i = 0; i &lt; rows.length; ++i) {
                      rows[i].style.display = '';
                    }
                }
                </script>
            </head>
            <body onload="toggleRows('showInformationRows', 'informationRow');toggleRows('showPassRows', 'passRow');">
                <xsl:call-template name="pageHeader"/>

                <xsl:call-template name="summary"/>

                <xsl:call-template name="classes"/>

            </body>
        </html>
    </xsl:template>

    <xsl:variable name="levelOrder">Failure|Warning|Information|Success</xsl:variable>

    <xsl:template name="classes">
        <xsl:for-each select="testsuite">
            <xsl:sort select="@name"/>
            <!-- create an anchor to this class name -->
            <a name="{@name}"></a>
            <h2>Quality Checks for
                <xsl:value-of select="@name"/>
            </h2>

            <p>
                <label><input id="showFailureRows" type="checkbox" checked="true" onclick="javascript:toggleRows('showFailureRows', 'failureRow');" />Show Error Rows</label>
                <label><input id="showWarningRows" type="checkbox" checked="true" onclick="javascript:toggleRows('showWarningRows', 'warningRow');" />Show Warning Rows</label>
                <label><input id="showInformationRows" type="checkbox" onclick="javascript:toggleRows('showInformationRows', 'informationRow');" />Show Information Rows</label>
                <label><input id="showPassRows" type="checkbox" onclick="javascript:toggleRows('showPassRows', 'passRow');" />Show Pass Rows</label>
            </p>

            <table>
                <xsl:call-template name="testcase.test.header"/>
                <!--
                test can even not be started at all (failure to load the class)
                so report the error directly
                -->
                <xsl:if test="./error">
                    <!--  <tr class="Error">-->
                    <tr>
                        <td colspan="4">
                            <xsl:apply-templates select="./error"/>
                        </td>
                    </tr>
                </xsl:if>
                <xsl:apply-templates select="./testcase" mode="print.test">
                    <xsl:sort select="@name" />
                </xsl:apply-templates>
            </table>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="summary">
        <h2>Summary</h2>
        <xsl:variable name="testCount" select="sum(testsuite/@tests)"/>
        <xsl:variable name="failureCount" select="count(//testsuite//testcase[failure])"/>
        <xsl:variable name="errorCount" select="count(//testsuite//testcase[error and not(failure)])"/>
        <xsl:variable name="timeCount" select="sum(testsuite/@time)"/>
        <xsl:variable name="successRate" select="($testCount - $failureCount - $errorCount) div $testCount"/>
        <table>
            <tr valign="top">
                <th>Tests</th>
                <th>Failures</th>
                <th>Warnings</th>
                <th>Success Rate</th>
            </tr>
            <tr valign="top">
                <xsl:attribute name="class">
                    <xsl:choose>
                        <xsl:when test="$failureCount &gt; 0">Failure</xsl:when>
                        <xsl:when test="$errorCount &gt; 0">Warning</xsl:when>
                    </xsl:choose>
                </xsl:attribute>
                <td>
                    <xsl:value-of select="$testCount"/>
                </td>
                <td>
                    <xsl:value-of select="$failureCount"/>
                </td>
                <td>
                    <xsl:value-of select="$errorCount"/>
                </td>
                <td>
                    <xsl:call-template name="display-percent">
                        <xsl:with-param name="value" select="$successRate"/>
                    </xsl:call-template>
                </td>
            </tr>
        </table>
    </xsl:template>

    <!-- Page HEADER -->
    <xsl:template name="pageHeader">
        <h1>Quality Check Report</h1>
        <p>
            This report presents the results of the automated Quality Checks when run against
            <b>
                <xsl:value-of select="$branchName"/>
            </b>
            at
            <b>
                <xsl:value-of select="$qaBuildTime"/>
            </b>
            .
            <br/>
            <br/>
            TeamCity Packaging Build Link:
            <a target="_blank"><xsl:attribute name="href">http://build.dev.cba/viewLog.html?buildId=<xsl:value-of select="$packagerBuildId"/></xsl:attribute>http://build.dev.cba/viewLog.html?buildId=<xsl:value-of select="$packagerBuildId"/></a>
            <br/>
            TeamCity Quality Checks Link:
            <a target="_blank"><xsl:attribute name="href">http://build.dev.cba/viewLog.html?buildId=<xsl:value-of select="$qaBuildId"/></xsl:attribute>http://build.dev.cba/viewLog.html?buildId=<xsl:value-of select="$qaBuildId"/></a>
            <br/>
        </p>
    </xsl:template>

    <xsl:template match="testsuite" mode="header">
        <tr valign="top">
            <th>Name</th>
            <th>Tests</th>
            <th>Warnings</th>
            <th>Failures</th>
            <th>Time(s)</th>
        </tr>
    </xsl:template>

    <!-- class header -->
    <xsl:template name="testsuite.test.header">
        <tr valign="top">
            <th>Name</th>
            <th>Tests</th>
            <th>Errors</th>
            <th>Warnings</th>
            <th>Time(s)</th>
            <th>Time Stamp</th>
            <th>Host</th>
        </tr>
    </xsl:template>

    <!-- method header -->
    <xsl:template name="testcase.test.header">
        <tr valign="top">
            <th>Artifact Name</th>
            <th>Status</th>
            <th>Detail</th>
        </tr>
    </xsl:template>

    <xsl:template match="testcase" mode="print.test">
        <tr valign="top">
            <xsl:attribute name="class">
            <xsl:choose>
                <xsl:when test="failure">failureRow</xsl:when>
                <xsl:when test="error">warningRow</xsl:when>
                <xsl:when test="system-out">informationRow</xsl:when>
                <xsl:otherwise>passRow</xsl:otherwise>
            </xsl:choose>
            </xsl:attribute>
            <td>
                <xsl:value-of select="@name"/>
                    <xsl:choose>
                        <xsl:when test="substring(@name,1,9) = '/TERADATA'">
                            (<a target="_blank"><xsl:attribute name="href">https://stash.odp.cba/projects/GDW/repos/gdw/browse<xsl:value-of select="@name"/>?at=refs%2Fheads%2F<xsl:value-of select="$branchName"/></xsl:attribute>Stash Link</a>)
                        </xsl:when>
                        <xsl:otherwise>
                            (<a target="_blank"><xsl:attribute name="href">http://build.dev.cba/repository/download/GDW_DeveloperTools_PackageTeradata/<xsl:value-of select="$packagerBuildId"/>:id/assembled_package.tgz</xsl:attribute>Package Link</a>)
                        </xsl:otherwise>
                    </xsl:choose>
            </td>
            <xsl:choose>
                <xsl:when test="failure and error">
                    <td><span class="Failure">Failure and Warning</span></td>
                    <td>
                        <p><xsl:apply-templates select="failure"/></p>
                        <p><xsl:apply-templates select="error"/></p>
                    </td>
                </xsl:when>
                <xsl:when test="failure and error and system-out">
                    <td><span class="Failure">Failure, Warning and Information</span></td>
                    <td>
                        <p><xsl:apply-templates select="failure"/></p>
                        <p><xsl:apply-templates select="error"/></p>
                        <p><xsl:call-template name="replaceCRwithBR">
                            <xsl:with-param name="text" select="system-out"/>
                        </xsl:call-template></p>
                    </td>
                </xsl:when>
                <xsl:when test="failure">
                    <td><span class="Failure">Failure</span></td>
                    <td>
                        <p><xsl:apply-templates select="failure"/></p>
                    </td>
                </xsl:when>
                <xsl:when test="error and system-out">
                    <td><span class="Warning">Warning and Information</span></td>
                    <td>
                        <p><xsl:apply-templates select="error"/></p>
                        <p><xsl:call-template name="replaceCRwithBR">
                            <xsl:with-param name="text" select="system-out"/>
                        </xsl:call-template></p>
                    </td>
                </xsl:when>
                <xsl:when test="error">
                    <td><span class="Warning">Warning</span></td>
                    <td>
                        <p><xsl:apply-templates select="error"/></p>
                    </td>
                </xsl:when>
                <xsl:when test="system-out">
                    <td><span class="Information">Information</span></td>
                    <td>
                        <p><xsl:call-template name="replaceCRwithBR">
                            <xsl:with-param name="text" select="system-out"/>
                        </xsl:call-template></p>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td><span>Success</span></td>
                    <td></td>
                </xsl:otherwise>
            </xsl:choose>
        </tr>
    </xsl:template>

    <xsl:template match="failure">
        <xsl:call-template name="display-failures"/>
    </xsl:template>

    <xsl:template match="error">
        <xsl:call-template name="display-failures"/>
    </xsl:template>

    <xsl:template name="display-failures">
        <xsl:choose>
            <xsl:when test="not(@message)">N/A</xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="injectConfluenceLinks">
                    <xsl:with-param name="text" select="@message"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="display-percent">
        <xsl:param name="value"/>
        <xsl:value-of select="format-number($value,'0.00%')"/>
    </xsl:template>

    <xsl:template name="injectConfluenceLinks">
        <xsl:param name="text"/>
        <xsl:param name="replace"/>
        <xsl:choose>
            <xsl:when test="contains($text, '[[')">
                <xsl:call-template name="replaceCRwithBR">
                    <xsl:with-param name="text" select="substring-before($text,'[[')"/>
                </xsl:call-template>
                <a target="_blank"><xsl:attribute name="href">http://knowit.cba/display/BICD/TEDS-160+%28Teradata+Quality+Assurance%29+-+Detailed+Requirements#TEDS-160(TeradataQualityAssurance)-DetailedRequirements-<xsl:value-of select="substring-before(substring-after($text,'[['),']]')"/></xsl:attribute>link to Confluence</a>
                <xsl:call-template name="injectConfluenceLinks">
                    <xsl:with-param name="text" select="substring-after($text,']]')"/>
                    <xsl:with-param name="replace" select="$replace"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="replaceCRwithBR">
                    <xsl:with-param name="text" select="$text"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="replaceCRwithBR">
        <xsl:param name="text"/>
        <xsl:choose>
            <xsl:when test="contains($text, '_BR_')">
                <xsl:value-of select="substring-before($text,'_BR_')"/>
                <br/>
                <xsl:call-template name="replaceCRwithBR">
                    <xsl:with-param name="text" select="substring-after($text,'_BR_')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$text"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
